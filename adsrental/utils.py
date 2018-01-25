import json

import requests
import boto3
from django.conf import settings
from django.apps import apps
import customerio
from shipstation.api import ShipStation, ShipStationOrder, ShipStationAddress, ShipStationItem, ShipStationWeight

from adsrental.models.customerio_event import CustomerIOEvent


class CustomerIOClient(object):
    def __init__(self):
        self.client = None
        if not settings.CUSTOMERIO_ENABLED:
            return
        self.client = customerio.CustomerIO(
            settings.CUSTOMERIO_SITE_ID, settings.CUSTOMERIO_API_KEY)

    def get_client(self):
        return self.client

    def send_lead(self, lead):
        if self.client:
            self.client.identify(
                id=lead.leadid,
                First_Name=lead.first_name,
                Last_Name=lead.last_name,
                email=lead.email,
                Company='[Empty]'
            )

    def send_lead_event(self, lead, event, **kwargs):
        CustomerIOEvent(
            lead=lead,
            name=event,
            kwargs=json.dumps(kwargs),
        ).save()
        if self.client:
            self.client.track(customer_id=lead.leadid, name=event, **kwargs)

    def is_enabled(self):
        return self.client is not None


class ShipStationClient(object):
    def __init__(self):
        self.client = ShipStation(
            key=settings.SHIPSTATION_API_KEY, secret=settings.SHIPSTATION_API_SECRET)

    def get_client(self):
        return self.client

    def add_sf_lead_order(self, sf_lead):
        order = ShipStationOrder(
            order_key=sf_lead.raspberry_pi.name, order_number=sf_lead.account_name)
        order.set_customer_details(
            username='{} {}'.format(sf_lead.first_name, sf_lead.last_name),
            email=sf_lead.email,
        )

        shipping_address = ShipStationAddress(
            name='{} {}'.format(sf_lead.first_name, sf_lead.last_name),
            # company=sf_lead.company,
            street1=sf_lead.street,
            city=sf_lead.city,
            postal_code=sf_lead.postal_code,
            # country=sf_lead.country,
            country='US',
            state=sf_lead.state,
            phone=sf_lead.phone or sf_lead.mobile_phone,
        )
        order.set_shipping_address(shipping_address)
        order.set_billing_address(shipping_address)

        item = ShipStationItem(
            name=sf_lead.raspberry_pi.name,
            quantity=1,
            unit_price=0,
        )
        item.set_weight(ShipStationWeight(units='ounces', value=0))
        order.add_item(item)

        order.set_status('awaiting_shipment')

        self.client.add_order(order)
        self.submit_orders()
        return order

    def submit_orders(self):
        for order in self.client.orders:
            self.post(
                endpoint='/orders/createorder',
                data=json.dumps(order.as_dict())
            )

    def post(self, endpoint='', data=None):
        url = '{}{}'.format(self.client.url, endpoint)
        headers = {'content-type': 'application/json'}
        r = requests.post(
            url,
            auth=(self.client.key, self.client.secret),
            data=data,
            headers=headers
        )
        if r.status_code not in [200, 201]:
            raise ValueError('Shipstation Error', r.status_code, r.text)

    def get_sf_lead_order_data(self, sf_lead):
        data = requests.get(
            'https://ssapi.shipstation.com/orders',
            params={'orderNumber': sf_lead.account_name},
            auth=requests.auth.HTTPBasicAuth(
                settings.SHIPSTATION_API_KEY, settings.SHIPSTATION_API_SECRET),
        ).json().get('orders')
        data = data[0] if data else None
        return data


class BotoResource(object):
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.resources = {}

    def get_resource(self, service='ec2'):
        if not self.resources.get(service):
            resource = self.session.resource(
                service, region_name=settings.AWS_REGION)
            self.resources[service] = resource

        return self.resources[service]

    def get_first_rpid_instance(self, rpid):
        instances = self.get_resource('ec2').instances.filter(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [rpid],
                },
            ],
        )
        instances_list = [i for i in instances]
        for instance in instances_list:
            instance_state = instance.state['Name']
            if self.get_instance_tag(instance, 'Duplicate') == 'true':
                continue

            if instance_state != 'running':
                continue

            return instance

        for instance in instances_list:
            if instance_state == 'terminated':
                continue

            if self.get_instance_tag(instance, 'Duplicate') == 'true':
                continue

            return instance

        for instance in instances_list:
            instance_state = instance.state['Name']
            if instance_state == 'terminated':
                continue
            return instance

        return False

    @staticmethod
    def get_instance_tag(instance, key):
        if not instance.tags:
            return None

        for tagpair in instance.tags:
            if tagpair['Key'] == key:
                return tagpair['Value']

        return None

    def set_instance_tag(self, instance, key, value):
        tags = instance.tags or []
        key_found = False
        for tagpair in tags:
            if tagpair['Key'] == key:
                key_found = True
                tagpair['Value'] = value
                break
        if not key_found:
            tags.append({'Key': key, 'Value': value})

        try:
            self.get_resource('ec2').create_tags(
                Resources=[instance.id], Tags=tags)
        except:
            print 'Cound not add tag for', instance.id, key, '=', value
            pass

    def launch_instance(self, rpid, email):
        instance = self.get_first_rpid_instance(rpid)
        if not instance:
            self.get_resource('ec2').create_instances(
                ImageId=settings.AWS_IMAGE_AMI,
                MinCount=1,
                MaxCount=1,
                KeyName='AI Farming Key',
                InstanceType='t2.micro',
                SecurityGroupIds=settings.AWS_SECURITY_GROUP_IDS,
                UserData=rpid,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': rpid,
                            },
                            {
                                'Key': 'Email',
                                'Value': email or '',
                            },
                            {
                                'Key': 'Duplicate',
                                'Value': 'false',
                            },
                        ]
                    },
                ],
            )
            instance = self.get_first_rpid_instance(rpid)
            if not instance:
                raise ValueError(instance)

        EC2Instance = apps.get_app_config('adsrental').get_model('EC2Instance')
        EC2Instance.upsert_from_boto(instance)
