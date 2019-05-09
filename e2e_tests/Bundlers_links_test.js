Feature('Admin banlinks Test')

Scenario('bunlinks', (I)=>{
    I.amOnPage('http://localhost:8443/app/admin/')
    I.see('Adsrental Administration')
    I.fillField('input[name="username"]', 'volshebnyi@gmail.com')
    I.fillField('input[name="password"]', 'team17')
    I.click('Log in')
    I.see('Dashboard')
    I.click('Bundlers')
    I.see('Select bundler to change')
    I.checkOption('input[name="_selected_action"]')
    I.click('Payments')
    I.see('Summary')
    I.click('Generate a new report')
    I.see('Reports')
    I.click('Preview new report')
    I.see('Summary')
    I.click('Generate a new report')
    I.see('New report was successfully generated')
    I.click('HTML')
    I.see('Summary')
    I.click('Admin')
    I.see('Dashboard')
    I.click('Bundlers')
    I.see('Select bundler to change')
    I.checkOption('input[name="_selected_action"]')
    I.click('Payments')
    I.see('Summary')
    I.click('Generate a new report')
    I.click('Send by email')
    I.see('Emails with report for 09 May 2019 were successfully sent')
    I.seeElement('span.glyphicon-ok')
    I.click('Admin')
    I.see('Dashboard')
    I.click('Bundlers')
    I.see('Select bundler to change')
    I.checkOption('input[name="_selected_action"]')
    I.click('Reports list')
    I.see('Reports for UTM source')
    I.click('Admin')
    I.see('Dashboard')
    I.click('Bundlers')
    I.see('Select bundler to change')
    I.checkOption('input[name="_selected_action"]')
    I.click('Leaderboard')
});