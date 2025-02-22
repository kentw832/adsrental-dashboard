Feature('Admin RaspberryPi Test')

Scenario('adrental active', (I)=>{
    I.amOnPage('http://localhost:8443/app/admin/')
    I.see('Adsrental Administration')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Log in')
    I.see('Dashboard')
    I.click('Raspberry pis')
    I.see('Select raspberry pi to change')
    I.fillField('input[name="q"]', 'RP999')
    I.click('Search')
    I.see('1 raspberry pi')
    I.checkOption('input[type="checkbox"]')
    I.fillField('select[name="action"]', 'Restart device')
    I.click('Go')
    I.checkOption('input[type="checkbox"]')
    I.fillField('select[name="action"]', 'Update config')
    I.click('Go')
    I.checkOption('input[type="checkbox"]')
    I.fillField('select[name="action"]', 'Reset cache')
    I.click('Go')
    I.checkOption('input[type="checkbox"]')
    I.fillField('select[name="action"]', 'Show cache')
    I.click('Go')
    I.checkOption('input[type="checkbox"]')
    I.fillField('select[name="action"]', 'Convert to proxy tunnel')
    I.click('Go')
    I.checkOption('input[type="checkbox"]')
    I.fillField('select[name="action"]', 'Convert to ec2')
    I.click('Go')

});
