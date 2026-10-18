# ScamGuard baseline evaluation

Generated: 2026-10-18T00:07:30.679117+00:00
Evaluation data: `data/eval/dev.csv` (90 examples)
Maximum false-positive rate for threshold selection: 5.0%

## Summary

| Model | Precision | Recall | F1 | FPR | FNR | Accuracy |
|---|---:|---:|---:|---:|---:|---:|
| always_scam | 46.7% | 100.0% | 63.6% | 100.0% | 0.0% | 46.7% |
| random_seed_0 | 41.1% | 54.8% | 46.9% | 68.8% | 45.2% | 42.2% |
| tfidf_logistic_regression | 68.4% | 31.0% | 42.6% | 12.5% | 69.0% | 61.1% |

## always_scam

Confusion matrix: TN=0, FP=48, FN=0, TP=42.
Recommended threshold at FPR <= 5.0%: 1.0000 (precision 0.0%, recall 0.0%).

### Per-channel breakdown

| Channel | Count | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 17 | 52.9% | 100.0% | 100.0% |
| email | 27 | 40.7% | 100.0% | 100.0% |
| other | 9 | 55.6% | 100.0% | 100.0% |
| sms | 29 | 34.5% | 100.0% | 100.0% |
| social | 8 | 87.5% | 100.0% | 100.0% |

### Misclassified examples

- `eval_133` actual=legit, predicted=scam, score=1.0000: Please review the incident summary by 3 PM; use the document already shared in our workspace.
- `eval_143` actual=legit, predicted=scam, score=1.0000: Community alert: the road closes at 6 PM for the parade, so move parked cars before then.
- `eval_121` actual=legit, predicted=scam, score=1.0000: Order update: the blue shirt is backordered. You will not be charged until it ships.
- `eval_074` actual=legit, predicted=scam, score=1.0000: Debit card alert: $8.60 was charged at City Café. We will never ask for your password or code.
- `eval_094` actual=legit, predicted=scam, score=1.0000: Delivery completed: your parcel was left in the building mailroom at 1:18 PM.
- `eval_073` actual=legit, predicted=scam, score=1.0000: Bank notice: a $75 transfer to your saved recipient completed. Review it in the mobile app if unexpected.
- `eval_128` actual=legit, predicted=scam, score=1.0000: My train was canceled. I booked another myself and will arrive at 9; no money needed.
- `eval_087` actual=legit, predicted=scam, score=1.0000: Code 508366 confirms your new device. Never send this code by text or email.
- `eval_129` actual=legit, predicted=scam, score=1.0000: Please bring the spare key to the house soon. I am waiting with the neighbor.
- `eval_098` actual=legit, predicted=scam, score=1.0000: Your pickup is ready at the parcel locker. Use code 1142 at the locker only.
- `eval_136` actual=legit, predicted=scam, score=1.0000: Urgent staffing update: the office closes at 4 because of weather. Take your laptop home.
- `eval_086` actual=legit, predicted=scam, score=1.0000: Your one-time code is 407255. Enter it only in the app you opened yourself.
- `eval_080` actual=legit, predicted=scam, score=1.0000: ATM withdrawal alert: $80 at 6:42 PM. Do not share one-time codes with anyone.
- `eval_078` actual=legit, predicted=scam, score=1.0000: Your credit card payment is due Friday. Autopay is scheduled; no action is needed.
- `eval_084` actual=legit, predicted=scam, score=1.0000: Use 205933 to finish signing in. Support will never ask you to read this code aloud.
- `eval_142` actual=legit, predicted=scam, score=1.0000: The meeting room changed to 3B. The start time remains 9 AM.
- `eval_146` actual=legit, predicted=scam, score=1.0000: Your streaming password was changed from the account settings. If you did this, no action is needed.
- `eval_105` actual=legit, predicted=scam, score=1.0000: Video appointment starts at 11 AM. Join from the patient portal you normally use.
- `eval_144` actual=legit, predicted=scam, score=1.0000: Free concert tickets are available from the library while supplies last; no payment or login is required.
- `eval_120` actual=legit, predicted=scam, score=1.0000: We received your return request. Print the label from the retailer account you used to order.
- `eval_145` actual=legit, predicted=scam, score=1.0000: The neighborhood group is collecting unopened food this weekend at the community center.
- `eval_134` actual=legit, predicted=scam, score=1.0000: Production is slow, but customer data is safe. Join the scheduled team call in ten minutes.
- `eval_101` actual=legit, predicted=scam, score=1.0000: Your grocery delivery driver is approaching. Please secure pets near the entrance.
- `eval_131` actual=legit, predicted=scam, score=1.0000: Can you call the pharmacy before it closes? The prescription needs a routine clarification.
- `eval_071` actual=legit, predicted=scam, score=1.0000: Card alert: $24.18 was approved at Corner Market. If you do not recognize it, open your banking app directly.
- `eval_077` actual=legit, predicted=scam, score=1.0000: Card-not-present purchase: $39.95. If this was not you, call the number printed on your card.
- `eval_102` actual=legit, predicted=scam, score=1.0000: Return received. Your refund will be processed to the original payment method.
- `eval_122` actual=legit, predicted=scam, score=1.0000: Payment received for order 8425. Refunds always return to the original payment method.
- `eval_123` actual=legit, predicted=scam, score=1.0000: Please call me when you see this. The school nurse needs an updated contact number, but everyone is safe.
- `eval_106` actual=legit, predicted=scam, score=1.0000: Reminder: vehicle service is booked Friday at 8 AM. Reply STOP to end reminders.
- `eval_089` actual=legit, predicted=scam, score=1.0000: Your workspace verification code is 710588. No employee will ask for it.
- `eval_138` actual=legit, predicted=scam, score=1.0000: The test environment is unavailable. Do not enter credentials into links sent outside this channel.
- `eval_141` actual=legit, predicted=scam, score=1.0000: Payroll closes at noon. Confirm your hours in the established employee portal.
- `eval_104` actual=legit, predicted=scam, score=1.0000: Your clinic visit is tomorrow at 2 PM. Bring your insurance card and arrive ten minutes early.
- `eval_139` actual=legit, predicted=scam, score=1.0000: Security drill at 2 PM: report the simulated message using the usual phishing button.
- `eval_103` actual=legit, predicted=scam, score=1.0000: Reminder: dental appointment Monday at 9:30 AM. Reply C to confirm or call 555-0120 to reschedule.
- `eval_116` actual=legit, predicted=scam, score=1.0000: Your monthly coffee subscription renews Monday for $16.00. Manage it from your account page.
- `eval_109` actual=legit, predicted=scam, score=1.0000: Therapy session reminder: Wednesday at 3 PM. Contact the office at 555-0126 with questions.
- `eval_127` actual=legit, predicted=scam, score=1.0000: The dog slipped out the gate. Please check the park now and message the family group if you see him.
- `eval_140` actual=legit, predicted=scam, score=1.0000: Call the on-duty manager at 555-0167 about the loading dock issue; do not send payment information.
- `eval_114` actual=legit, predicted=scam, score=1.0000: Your grocery order is being prepared. One item was unavailable and has been refunded.
- `eval_137` actual=legit, predicted=scam, score=1.0000: Please approve the corrected invoice in our normal accounting system before today's cutoff.
- `eval_149` actual=legit, predicted=scam, score=1.0000: Marketplace update: your buyer canceled, and no funds changed hands. Keep all messages in the app.
- `eval_130` actual=legit, predicted=scam, score=1.0000: Dad's flight changed. Check the itinerary in our shared calendar before leaving for the airport.
- `eval_124` actual=legit, predicted=scam, score=1.0000: Can you pick up the kids by 5? My meeting ran late. Call me on our usual number if you cannot.
- `eval_083` actual=legit, predicted=scam, score=1.0000: Your sign-in code is 104822. It expires in ten minutes. Do not share this code with anyone.
- `eval_111` actual=legit, predicted=scam, score=1.0000: Reservation confirmed for four guests at 7 PM tonight. Reply CANCEL if plans changed.
- `eval_072` actual=legit, predicted=scam, score=1.0000: Checking alert: your scheduled rent payment of $1,240 posted this morning. No action is required.

## random_seed_0

Confusion matrix: TN=15, FP=33, FN=19, TP=23.
Recommended threshold at FPR <= 5.0%: 0.9675 (precision 50.0%, recall 2.4%).

### Per-channel breakdown

| Channel | Count | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 17 | 30.0% | 33.3% | 87.5% |
| email | 27 | 37.5% | 54.5% | 62.5% |
| other | 9 | 50.0% | 40.0% | 50.0% |
| sms | 29 | 40.9% | 90.0% | 68.4% |
| social | 8 | 75.0% | 42.9% | 100.0% |

### Misclassified examples

- `eval_035` actual=scam, predicted=legit, score=0.4206: Your grandson asked me to message. Wire funds within an hour and do not call him because police have his phone.
- `eval_143` actual=legit, predicted=scam, score=0.5113: Community alert: the road closes at 6 PM for the parade, so move parked cars before then.
- `eval_074` actual=legit, predicted=scam, score=0.7838: Debit card alert: $8.60 was charged at City Café. We will never ask for your password or code.
- `eval_040` actual=scam, predicted=legit, score=0.3033: Your résumé was selected for an executive role. Send your verification code and account login today.
- `eval_073` actual=legit, predicted=scam, score=0.5834: Bank notice: a $75 transfer to your saved recipient completed. Review it in the mobile app if unexpected.
- `eval_128` actual=legit, predicted=scam, score=0.9081: My train was canceled. I booked another myself and will arrive at 9; no money needed.
- `eval_026` actual=scam, predicted=legit, score=0.2818: My love, do not mention this to your family. I need gift cards for an emergency ticket.
- `eval_087` actual=legit, predicted=scam, score=0.6184: Code 508366 confirms your new device. Never send this code by text or email.
- `eval_098` actual=legit, predicted=scam, score=0.9828: Your pickup is ready at the parcel locker. Use code 1142 at the locker only.
- `eval_136` actual=legit, predicted=scam, score=0.9022: Urgent staffing update: the office closes at 4 because of weather. Take your laptop home.
- `eval_080` actual=legit, predicted=scam, score=0.7298: ATM withdrawal alert: $80 at 6:42 PM. Do not share one-time codes with anyone.
- `eval_006` actual=scam, predicted=legit, score=0.4721: Your express shipment has incomplete postage. Resolve it now at https://postage-check.example.org/609.
- `eval_142` actual=legit, predicted=scam, score=0.6109: The meeting room changed to 3B. The start time remains 9 AM.
- `eval_146` actual=legit, predicted=scam, score=0.9130: Your streaming password was changed from the account settings. If you did this, no action is needed.
- `eval_105` actual=legit, predicted=scam, score=0.9666: Video appointment starts at 11 AM. Join from the patient portal you normally use.
- `eval_003` actual=scam, predicted=legit, score=0.4770: We could not leave your package. Choose a new time within two hours: https://delivery-slot.example.org/306.
- `eval_144` actual=legit, predicted=scam, score=0.8653: Free concert tickets are available from the library while supplies last; no payment or login is required.
- `eval_046` actual=scam, predicted=legit, score=0.2605: Rewards committee notice: buy a gift card for processing or your cash prize goes to someone else.
- `eval_120` actual=legit, predicted=scam, score=0.5487: We received your return request. Print the label from the retailer account you used to order.
- `eval_134` actual=legit, predicted=scam, score=0.7197: Production is slow, but customer data is safe. Join the scheduled team call in ten minutes.
- `eval_131` actual=legit, predicted=scam, score=0.8248: Can you call the pharmacy before it closes? The prescription needs a routine clarification.
- `eval_071` actual=legit, predicted=scam, score=0.6682: Card alert: $24.18 was approved at Corner Market. If you do not recognize it, open your banking app directly.
- `eval_027` actual=scam, predicted=legit, score=0.0011: Our connection is special. Send crypto tonight, and please keep the transfer between us.
- `eval_049` actual=scam, predicted=legit, score=0.4936: Move to encrypted chat for a guaranteed investment slot, then wire your funds before noon.
- `eval_077` actual=legit, predicted=scam, score=0.8676: Card-not-present purchase: $39.95. If this was not you, call the number printed on your card.
- `eval_123` actual=legit, predicted=scam, score=0.8705: Please call me when you see this. The school nurse needs an updated contact number, but everyone is safe.
- `eval_051` actual=scam, predicted=legit, score=0.1911: Limited presale access guarantees profit. Leave the forum and send your wallet deposit now.
- `eval_106` actual=legit, predicted=scam, score=0.5675: Reminder: vehicle service is booked Friday at 8 AM. Reply STOP to end reminders.
- `eval_020` actual=scam, predicted=legit, score=0.0804: Cloud help desk: your files are being deleted. Send your password immediately so we can stop the process.
- `eval_057` actual=scam, predicted=legit, score=0.3201: My business account requires your verification code. Leave the platform and send it immediately.
- `eval_141` actual=legit, predicted=scam, score=0.5079: Payroll closes at noon. Confirm your hours in the established employee portal.
- `eval_104` actual=legit, predicted=scam, score=0.9328: Your clinic visit is tomorrow at 2 PM. Bring your insurance card and arrive ten minutes early.
- `eval_036` actual=scam, predicted=legit, score=0.1091: You are hired for a remote assistant role at $90 an hour. Send your bank password today to start.
- `eval_139` actual=legit, predicted=scam, score=0.7066: Security drill at 2 PM: report the simulated message using the usual phishing button.
- `eval_103` actual=legit, predicted=scam, score=0.5403: Reminder: dental appointment Monday at 9:30 AM. Reply C to confirm or call 555-0120 to reschedule.
- `eval_116` actual=legit, predicted=scam, score=0.9638: Your monthly coffee subscription renews Monday for $16.00. Manage it from your account page.
- `eval_109` actual=legit, predicted=scam, score=0.5876: Therapy session reminder: Wednesday at 3 PM. Contact the office at 555-0126 with questions.
- `eval_041` actual=scam, predicted=legit, score=0.4450: Start work tonight and keep the excess from our check. First, return the balance through Zelle.
- `eval_127` actual=legit, predicted=scam, score=0.5963: The dog slipped out the gate. Please check the park now and message the family group if you see him.
- `eval_012` actual=scam, predicted=legit, score=0.3849: Unusual card activity requires immediate review. Sign in through https://fraud-review.example.com/013.
- `eval_140` actual=legit, predicted=scam, score=0.5757: Call the on-duty manager at 555-0167 about the loading dock issue; do not send payment information.
- `eval_061` actual=scam, predicted=legit, score=0.2903: Internet provider collections: send Zelle immediately or technicians will disconnect service.
- `eval_064` actual=scam, predicted=legit, score=0.1894: Utility final warning: make an immediate wire payment to prevent disconnection.
- `eval_033` actual=scam, predicted=legit, score=0.1867: Auntie, I am in trouble overseas. Send crypto right now and do not contact my parents.
- `eval_114` actual=legit, predicted=scam, score=0.6567: Your grocery order is being prepared. One item was unavailable and has been refunded.
- `eval_015` actual=scam, predicted=legit, score=0.0898: Benefits agency alert: your account is suspended. Send payment by Zelle today to restore it.
- `eval_149` actual=legit, predicted=scam, score=0.9234: Marketplace update: your buyer canceled, and no funds changed hands. Keep all messages in the app.
- `eval_130` actual=legit, predicted=scam, score=0.8425: Dad's flight changed. Check the itinerary in our shared calendar before leaving for the airport.
- `eval_124` actual=legit, predicted=scam, score=0.9231: Can you pick up the kids by 5? My meeting ran late. Call me on our usual number if you cannot.
- `eval_083` actual=legit, predicted=scam, score=0.5406: Your sign-in code is 104822. It expires in ten minutes. Do not share this code with anyone.
- `eval_019` actual=scam, predicted=legit, score=0.3913: Device support detected a severe infection. Install our remote access tool now so a technician can clean it.
- `eval_072` actual=legit, predicted=scam, score=0.5898: Checking alert: your scheduled rent payment of $1,240 posted this morning. No action is required.

## tfidf_logistic_regression

Confusion matrix: TN=42, FP=6, FN=29, TP=13.
Recommended threshold at FPR <= 5.0%: 0.6181 (precision 80.0%, recall 19.0%).

### Per-channel breakdown

| Channel | Count | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 17 | 75.0% | 33.3% | 12.5% |
| email | 27 | 83.3% | 45.5% | 6.2% |
| other | 9 | 100.0% | 20.0% | 0.0% |
| sms | 29 | 50.0% | 40.0% | 21.1% |
| social | 8 | 0.0% | 0.0% | 0.0% |

### Misclassified examples

- `eval_068` actual=scam, predicted=legit, score=0.4074: School administrator: open https://student-notice.example.com/421 and enter your login before classes are dropped.
- `eval_035` actual=scam, predicted=legit, score=0.3588: Your grandson asked me to message. Wire funds within an hour and do not call him because police have his phone.
- `eval_026` actual=scam, predicted=legit, score=0.2633: My love, do not mention this to your family. I need gift cards for an emergency ticket.
- `eval_055` actual=scam, predicted=legit, score=0.1371: I sent a courier fee by mistake. Wire it back today outside the marketplace app.
- `eval_087` actual=legit, predicted=scam, score=0.8689: Code 508366 confirms your new device. Never send this code by text or email.
- `eval_034` actual=scam, predicted=legit, score=0.1169: Dad, please pay my emergency bill through Zelle. I am embarrassed, so keep this secret.
- `eval_010` actual=scam, predicted=legit, score=0.3965: We detected a new device. Confirm your password today at https://bank-session.example.org/912 or access will close.
- `eval_006` actual=scam, predicted=legit, score=0.2863: Your express shipment has incomplete postage. Resolve it now at https://postage-check.example.org/609.
- `eval_003` actual=scam, predicted=legit, score=0.4573: We could not leave your package. Choose a new time within two hours: https://delivery-slot.example.org/306.
- `eval_144` actual=legit, predicted=scam, score=0.5249: Free concert tickets are available from the library while supplies last; no payment or login is required.
- `eval_067` actual=scam, predicted=legit, score=0.3051: Streaming account team: verify your password within one hour at https://media-login.example.org/320.
- `eval_120` actual=legit, predicted=scam, score=0.5557: We received your return request. Print the label from the retailer account you used to order.
- `eval_027` actual=scam, predicted=legit, score=0.3415: Our connection is special. Send crypto tonight, and please keep the transfer between us.
- `eval_106` actual=legit, predicted=scam, score=0.7990: Reminder: vehicle service is booked Friday at 8 AM. Reply STOP to end reminders.
- `eval_038` actual=scam, predicted=legit, score=0.3688: Earn $4,000 weekly from home with no interview. Pay the crypto onboarding fee before midnight.
- `eval_020` actual=scam, predicted=legit, score=0.4432: Cloud help desk: your files are being deleted. Send your password immediately so we can stop the process.
- `eval_057` actual=scam, predicted=legit, score=0.2963: My business account requires your verification code. Leave the platform and send it immediately.
- `eval_036` actual=scam, predicted=legit, score=0.4580: You are hired for a remote assistant role at $90 an hour. Send your bank password today to start.
- `eval_017` actual=scam, predicted=legit, score=0.4696: Immigration fee notice: immediate crypto payment is required or your application will be denied.
- `eval_029` actual=scam, predicted=legit, score=0.0815: I trust only you. Secretly buy a gift card so I can pay the clinic and come home.
- `eval_103` actual=legit, predicted=scam, score=0.6172: Reminder: dental appointment Monday at 9:30 AM. Reply C to confirm or call 555-0120 to reschedule.
- `eval_116` actual=legit, predicted=scam, score=0.5912: Your monthly coffee subscription renews Monday for $16.00. Manage it from your account page.
- `eval_024` actual=scam, predicted=legit, score=0.4597: Mailbox technical team: approve the remote session now or today's messages will be lost.
- `eval_041` actual=scam, predicted=legit, score=0.2719: Start work tonight and keep the excess from our check. First, return the balance through Zelle.
- `eval_012` actual=scam, predicted=legit, score=0.3268: Unusual card activity requires immediate review. Sign in through https://fraud-review.example.com/013.
- `eval_064` actual=scam, predicted=legit, score=0.3464: Utility final warning: make an immediate wire payment to prevent disconnection.
- `eval_033` actual=scam, predicted=legit, score=0.1320: Auntie, I am in trouble overseas. Send crypto right now and do not contact my parents.
- `eval_023` actual=scam, predicted=legit, score=0.1178: Support agent here. Tell me your administrator password so I can remove the account breach.
- `eval_015` actual=scam, predicted=legit, score=0.4961: Benefits agency alert: your account is suspended. Send payment by Zelle today to restore it.
- `eval_069` actual=scam, predicted=legit, score=0.2106: Insurance claims desk: your coverage ends today unless you confirm at https://policy-check.example.net/522.
- `eval_004` actual=scam, predicted=legit, score=0.4738: Final carrier reminder: your shipment will be returned tonight unless you verify at https://track-now.example.com/407.
- `eval_019` actual=scam, predicted=legit, score=0.2090: Device support detected a severe infection. Install our remote access tool now so a technician can clean it.
- `eval_066` actual=scam, predicted=legit, score=0.2184: Parking office: your vehicle registration will be suspended unless you settle at https://parking-case.example.net/219.
- `eval_002` actual=scam, predicted=legit, score=0.4162: Delivery notice: a 42-cent redelivery fee is due today. Update at https://courier-help.example.net/redo/205.
- `eval_062` actual=scam, predicted=legit, score=0.3872: Gas service notice: pay in crypto today to avoid a safety lock at your address.

Full threshold sweeps, per-category metrics, and tactic metrics are in the JSON report.
