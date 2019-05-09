Feature('Admin fix Test')

Scenario('fix', (I)=>{
    I.amOnPage('http://localhost:8443/app/admin/')
    I.see('Adsrental Administration')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Log in')
    I.see('Dashboard')
    I.click('Lead accounts')
    I.see('Select lead account to change')
    I.click('Report new issue')
    I.see('Report issue for')
    I.fillField('select[name="issue_type"]', 'Ban Account Request')
    I.fillField('textarea[name="note"]', 'account ban')
    I.click('Report')
    I.checkOption('input[name="_selected_action"')
    I.click('Fix')
    I.see('Fix Ban Account')
    I.fillField('textarea[name="note"]', 'no ban reason')
    I.click('Fix')
    I.see('Fix')
    I.click('Resolve / Reject as admin')
    I.see('Resolve Ban Accoun')
    I.fillField('textarea[name="note"]', 'fixed')
    I.click('Resolve')
    I.see('New value')
    I.see('account ban')
    I.see('no ban reason')
    I.see('fixed')
    I.click('Home')
    I.see('Dashboard')
    I.click('Lead accounts')
    I.see('Select lead account to change')
    I.click('Report new issue')
    I.see('Report issue for')
    I.fillField('select[name="issue_type"]', 'Security Checkpoint')
    I.fillField('textarea[name="note"]', 'does not work')
    I.click('Report')
    I.checkOption('input[name="_selected_action"')
    I.click('Fix')
    I.see('Fix Security Checkpoint')
    I.fillField('textarea[name="note"]', 'checkpoint')
    I.click('Fix')
    I.see('Fix')
    I.click('Resolve / Reject as admin')
    I.see('Resolve Security Checkpoint')
    I.fillField('textarea[name="note"]', 'fixed')
    I.click('Resolve')
    I.see('New value')
    I.see('does not work')
    I.see('checkpoint')
    I.see('fixed')
    I.click('Home')
    I.see('Dashboard')
    I.click('Lead accounts')
    I.see('Select lead account to change')
    I.click('Report new issue')
    I.see('Report issue for')
    I.fillField('select[name="issue_type"]', 'Missing Payment')
    I.fillField('textarea[name="note"]', 'did not recieve payment')
    I.click('Report')
    I.checkOption('input[name="_selected_action"')
    I.click('Fix')
    I.see('Fix Missing Payment')
    I.fillField('textarea[name="note"]', 'payment')
    I.click('Fix')
    I.see('Fix Missing Payment ')
    I.click('Resolve / Reject as admin')
    I.see('Resolve Missing Payment')
    I.fillField('textarea[name="note"]', 'fixed')
    I.click('Resolve')
    I.see('New value')
    I.see('did not recieve payment')
    I.see('payment')
    I.see('fixed')

    



});
