# ScamGuard baseline evaluation

Generated: 2026-10-16T23:40:52.285425+00:00
Evaluation data: `data/eval/test_set.csv` (150 examples)
Maximum false-positive rate for threshold selection: 5.0%

## Summary

| Model | Precision | Recall | F1 | FPR | FNR | Accuracy |
|---|---:|---:|---:|---:|---:|---:|
| always_scam | 46.7% | 100.0% | 63.6% | 100.0% | 0.0% | 46.7% |
| random_seed_0 | 48.8% | 60.0% | 53.8% | 55.0% | 40.0% | 52.0% |
| tfidf_logistic_regression | 65.5% | 27.1% | 38.4% | 12.5% | 72.9% | 59.3% |

## always_scam

Confusion matrix: TN=0, FP=80, FN=0, TP=70.
Recommended threshold at FPR <= 5.0%: 1.0000 (precision 0.0%, recall 0.0%).

### Per-channel breakdown

| Channel | Count | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 29 | 55.2% | 100.0% | 100.0% |
| email | 46 | 41.3% | 100.0% | 100.0% |
| other | 14 | 50.0% | 100.0% | 100.0% |
| sms | 47 | 34.0% | 100.0% | 100.0% |
| social | 14 | 85.7% | 100.0% | 100.0% |

### Misclassified examples

- `eval_071` actual=legit, predicted=scam, score=1.0000: Card alert: $24.18 was approved at Corner Market. If you do not recognize it, open your banking app directly.
- `eval_072` actual=legit, predicted=scam, score=1.0000: Checking alert: your scheduled rent payment of $1,240 posted this morning. No action is required.
- `eval_073` actual=legit, predicted=scam, score=1.0000: Bank notice: a $75 transfer to your saved recipient completed. Review it in the mobile app if unexpected.
- `eval_074` actual=legit, predicted=scam, score=1.0000: Debit card alert: $8.60 was charged at City Café. We will never ask for your password or code.
- `eval_075` actual=legit, predicted=scam, score=1.0000: Your balance fell below the alert level you selected. Sign in through your usual app to review activity.
- `eval_076` actual=legit, predicted=scam, score=1.0000: Deposit confirmed: $620.00 was added to checking. This automated message cannot accept replies.
- `eval_077` actual=legit, predicted=scam, score=1.0000: Card-not-present purchase: $39.95. If this was not you, call the number printed on your card.
- `eval_078` actual=legit, predicted=scam, score=1.0000: Your credit card payment is due Friday. Autopay is scheduled; no action is needed.
- `eval_079` actual=legit, predicted=scam, score=1.0000: Fraud monitor declined a $410 purchase. Open your bank app directly if you made it.
- `eval_080` actual=legit, predicted=scam, score=1.0000: ATM withdrawal alert: $80 at 6:42 PM. Do not share one-time codes with anyone.
- `eval_081` actual=legit, predicted=scam, score=1.0000: A recurring subscription charged $12.99 today. Manage merchants inside your banking app.
- `eval_082` actual=legit, predicted=scam, score=1.0000: Your monthly statement is ready. Use your saved bookmark or mobile app to view it.
- `eval_083` actual=legit, predicted=scam, score=1.0000: Your sign-in code is 104822. It expires in ten minutes. Do not share this code with anyone.
- `eval_084` actual=legit, predicted=scam, score=1.0000: Use 205933 to finish signing in. Support will never ask you to read this code aloud.
- `eval_085` actual=legit, predicted=scam, score=1.0000: Verification code: 306144. If you did not request it, ignore this message and change your password in the app.
- `eval_086` actual=legit, predicted=scam, score=1.0000: Your one-time code is 407255. Enter it only in the app you opened yourself.
- `eval_087` actual=legit, predicted=scam, score=1.0000: Code 508366 confirms your new device. Never send this code by text or email.
- `eval_088` actual=legit, predicted=scam, score=1.0000: Login code: 609477. It expires in five minutes and cannot be reused.
- `eval_089` actual=legit, predicted=scam, score=1.0000: Your workspace verification code is 710588. No employee will ask for it.
- `eval_090` actual=legit, predicted=scam, score=1.0000: Use code 811699 to approve your own sign-in. If this was not you, deny the request in the app.
- `eval_091` actual=legit, predicted=scam, score=1.0000: Two-step verification code: 912700. Keep it private.
- `eval_092` actual=legit, predicted=scam, score=1.0000: Code 013811 was requested for your account. Ignore it if you did not initiate a login.
- `eval_093` actual=legit, predicted=scam, score=1.0000: Your package is out for delivery today between 2 and 5 PM. No signature is required.
- `eval_094` actual=legit, predicted=scam, score=1.0000: Delivery completed: your parcel was left in the building mailroom at 1:18 PM.
- `eval_095` actual=legit, predicted=scam, score=1.0000: Your order shipped and is expected Tuesday. Track it from your original order confirmation.
- `eval_096` actual=legit, predicted=scam, score=1.0000: Courier update: weather delayed today's route. A new delivery estimate will appear tomorrow.
- `eval_097` actual=legit, predicted=scam, score=1.0000: A signature will be required for tomorrow's delivery. No payment is due.
- `eval_098` actual=legit, predicted=scam, score=1.0000: Your pickup is ready at the parcel locker. Use code 1142 at the locker only.
- `eval_099` actual=legit, predicted=scam, score=1.0000: Delivery attempt missed. Reschedule from the retailer app where you placed the order.
- `eval_100` actual=legit, predicted=scam, score=1.0000: Package 2253 is moving through the regional facility and remains on schedule.
- `eval_101` actual=legit, predicted=scam, score=1.0000: Your grocery delivery driver is approaching. Please secure pets near the entrance.
- `eval_102` actual=legit, predicted=scam, score=1.0000: Return received. Your refund will be processed to the original payment method.
- `eval_103` actual=legit, predicted=scam, score=1.0000: Reminder: dental appointment Monday at 9:30 AM. Reply C to confirm or call 555-0120 to reschedule.
- `eval_104` actual=legit, predicted=scam, score=1.0000: Your clinic visit is tomorrow at 2 PM. Bring your insurance card and arrive ten minutes early.
- `eval_105` actual=legit, predicted=scam, score=1.0000: Video appointment starts at 11 AM. Join from the patient portal you normally use.
- `eval_106` actual=legit, predicted=scam, score=1.0000: Reminder: vehicle service is booked Friday at 8 AM. Reply STOP to end reminders.
- `eval_107` actual=legit, predicted=scam, score=1.0000: Your parent-teacher conference is Thursday at 4:15 PM in room 204.
- `eval_108` actual=legit, predicted=scam, score=1.0000: Haircut appointment confirmed for Saturday at 10 AM. No deposit is due.
- `eval_109` actual=legit, predicted=scam, score=1.0000: Therapy session reminder: Wednesday at 3 PM. Contact the office at 555-0126 with questions.
- `eval_110` actual=legit, predicted=scam, score=1.0000: Your annual checkup is next week. Complete forms in the clinic app before arrival.
- `eval_111` actual=legit, predicted=scam, score=1.0000: Reservation confirmed for four guests at 7 PM tonight. Reply CANCEL if plans changed.
- `eval_112` actual=legit, predicted=scam, score=1.0000: Reminder from the library: your study room reservation begins in 30 minutes.
- `eval_113` actual=legit, predicted=scam, score=1.0000: Order confirmed: two notebooks, total $18.42. We will email again when it ships.
- `eval_114` actual=legit, predicted=scam, score=1.0000: Your grocery order is being prepared. One item was unavailable and has been refunded.
- `eval_115` actual=legit, predicted=scam, score=1.0000: Receipt for your bookstore purchase: $31.70 paid with the card ending 0142.
- `eval_116` actual=legit, predicted=scam, score=1.0000: Your monthly coffee subscription renews Monday for $16.00. Manage it from your account page.
- `eval_117` actual=legit, predicted=scam, score=1.0000: Order 7314 has shipped. The delivery address matches the one saved during checkout.
- `eval_118` actual=legit, predicted=scam, score=1.0000: Thanks for your purchase. Your digital receipt is attached; no reply is needed.
- `eval_119` actual=legit, predicted=scam, score=1.0000: Your restaurant pickup will be ready at 6:20 PM under the name Customer.
- `eval_120` actual=legit, predicted=scam, score=1.0000: We received your return request. Print the label from the retailer account you used to order.
- `eval_121` actual=legit, predicted=scam, score=1.0000: Order update: the blue shirt is backordered. You will not be charged until it ships.
- `eval_122` actual=legit, predicted=scam, score=1.0000: Payment received for order 8425. Refunds always return to the original payment method.
- `eval_123` actual=legit, predicted=scam, score=1.0000: Please call me when you see this. The school nurse needs an updated contact number, but everyone is safe.
- `eval_124` actual=legit, predicted=scam, score=1.0000: Can you pick up the kids by 5? My meeting ran late. Call me on our usual number if you cannot.
- `eval_125` actual=legit, predicted=scam, score=1.0000: Urgent: the basement pipe is leaking. I shut off the water; please bring towels when you get home.
- `eval_126` actual=legit, predicted=scam, score=1.0000: I am at the clinic with Grandma. She is stable, and I will call after the doctor finishes.
- `eval_127` actual=legit, predicted=scam, score=1.0000: The dog slipped out the gate. Please check the park now and message the family group if you see him.
- `eval_128` actual=legit, predicted=scam, score=1.0000: My train was canceled. I booked another myself and will arrive at 9; no money needed.
- `eval_129` actual=legit, predicted=scam, score=1.0000: Please bring the spare key to the house soon. I am waiting with the neighbor.
- `eval_130` actual=legit, predicted=scam, score=1.0000: Dad's flight changed. Check the itinerary in our shared calendar before leaving for the airport.
- `eval_131` actual=legit, predicted=scam, score=1.0000: Can you call the pharmacy before it closes? The prescription needs a routine clarification.
- `eval_132` actual=legit, predicted=scam, score=1.0000: The smoke alarm is chirping again. Please pick up batteries on your way home.
- `eval_133` actual=legit, predicted=scam, score=1.0000: Please review the incident summary by 3 PM; use the document already shared in our workspace.
- `eval_134` actual=legit, predicted=scam, score=1.0000: Production is slow, but customer data is safe. Join the scheduled team call in ten minutes.
- `eval_135` actual=legit, predicted=scam, score=1.0000: The client moved tomorrow's deadline forward. Reply in this thread with your realistic estimate.
- `eval_136` actual=legit, predicted=scam, score=1.0000: Urgent staffing update: the office closes at 4 because of weather. Take your laptop home.
- `eval_137` actual=legit, predicted=scam, score=1.0000: Please approve the corrected invoice in our normal accounting system before today's cutoff.
- `eval_138` actual=legit, predicted=scam, score=1.0000: The test environment is unavailable. Do not enter credentials into links sent outside this channel.
- `eval_139` actual=legit, predicted=scam, score=1.0000: Security drill at 2 PM: report the simulated message using the usual phishing button.
- `eval_140` actual=legit, predicted=scam, score=1.0000: Call the on-duty manager at 555-0167 about the loading dock issue; do not send payment information.
- `eval_141` actual=legit, predicted=scam, score=1.0000: Payroll closes at noon. Confirm your hours in the established employee portal.
- `eval_142` actual=legit, predicted=scam, score=1.0000: The meeting room changed to 3B. The start time remains 9 AM.
- `eval_143` actual=legit, predicted=scam, score=1.0000: Community alert: the road closes at 6 PM for the parade, so move parked cars before then.
- `eval_144` actual=legit, predicted=scam, score=1.0000: Free concert tickets are available from the library while supplies last; no payment or login is required.
- `eval_145` actual=legit, predicted=scam, score=1.0000: The neighborhood group is collecting unopened food this weekend at the community center.
- `eval_146` actual=legit, predicted=scam, score=1.0000: Your streaming password was changed from the account settings. If you did this, no action is needed.
- `eval_147` actual=legit, predicted=scam, score=1.0000: School is closed today because of ice. Updates will be posted on the district's usual channel.
- `eval_148` actual=legit, predicted=scam, score=1.0000: Reminder: utility crews will test alarms at noon. Your service will not be disconnected.
- `eval_149` actual=legit, predicted=scam, score=1.0000: Marketplace update: your buyer canceled, and no funds changed hands. Keep all messages in the app.
- `eval_150` actual=legit, predicted=scam, score=1.0000: Your friend shared a photo album at https://photos.example.org/family; the link was created from your shared account.

## random_seed_0

Confusion matrix: TN=36, FP=44, FN=28, TP=42.
Recommended threshold at FPR <= 5.0%: 0.9638 (precision 57.1%, recall 5.7%).

### Per-channel breakdown

| Channel | Count | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 29 | 58.8% | 62.5% | 53.8% |
| email | 46 | 44.4% | 63.2% | 55.6% |
| other | 14 | 66.7% | 85.7% | 42.9% |
| sms | 47 | 35.7% | 62.5% | 58.1% |
| social | 14 | 80.0% | 33.3% | 50.0% |

### Misclassified examples

- `eval_003` actual=scam, predicted=legit, score=0.4206: We could not leave your package. Choose a new time within two hours: https://delivery-slot.example.org/306.
- `eval_004` actual=scam, predicted=legit, score=0.2589: Final carrier reminder: your shipment will be returned tonight unless you verify at https://track-now.example.com/407.
- `eval_006` actual=scam, predicted=legit, score=0.4049: Your express shipment has incomplete postage. Resolve it now at https://postage-check.example.org/609.
- `eval_008` actual=scam, predicted=legit, score=0.3033: Fraud desk: we blocked a purchase. Reply with the six-digit code we sent so we can cancel it immediately.
- `eval_009` actual=scam, predicted=legit, score=0.4766: Your checking access expires in 30 minutes. Restore it at https://account-verify.example.net/811.
- `eval_013` actual=scam, predicted=legit, score=0.2818: Revenue office: an arrest notice will be filed today unless you pay the balance with gift cards.
- `eval_016` actual=scam, predicted=legit, score=0.2505: Tax investigator assigned to case 2041. Buy two gift cards now and call 555-0104 with the numbers.
- `eval_021` actual=scam, predicted=legit, score=0.3101: Security center calling from 555-0106: share the code on your screen before the warning expires.
- `eval_025` actual=scam, predicted=legit, score=0.4721: I feel closer to you every day. Please keep us private and wire money so I can finally visit.
- `eval_026` actual=scam, predicted=legit, score=0.1007: My love, do not mention this to your family. I need gift cards for an emergency ticket.
- `eval_027` actual=scam, predicted=legit, score=0.4342: Our connection is special. Send crypto tonight, and please keep the transfer between us.
- `eval_031` actual=scam, predicted=legit, score=0.4770: Grandpa, I had an accident. Wire bail money immediately and keep it from the rest of the family.
- `eval_033` actual=scam, predicted=legit, score=0.2605: Auntie, I am in trouble overseas. Send crypto right now and do not contact my parents.
- `eval_036` actual=scam, predicted=legit, score=0.0140: You are hired for a remote assistant role at $90 an hour. Send your bank password today to start.
- `eval_038` actual=scam, predicted=legit, score=0.3988: Earn $4,000 weekly from home with no interview. Pay the crypto onboarding fee before midnight.
- `eval_041` actual=scam, predicted=legit, score=0.0011: Start work tonight and keep the excess from our check. First, return the balance through Zelle.
- `eval_042` actual=scam, predicted=legit, score=0.4936: Prize office: you won $50,000 without entering. Pay the gift-card release fee today.
- `eval_044` actual=scam, predicted=legit, score=0.2439: Lottery claims desk: send crypto now to unlock your unclaimed jackpot.
- `eval_045` actual=scam, predicted=legit, score=0.3252: You are our surprise millionth visitor. Pay by Zelle before midnight to receive the award.
- `eval_047` actual=scam, predicted=legit, score=0.1911: Guaranteed 30% crypto return this week. Leave this app and message me privately to deposit now.
- `eval_049` actual=scam, predicted=legit, score=0.2386: Move to encrypted chat for a guaranteed investment slot, then wire your funds before noon.
- `eval_052` actual=scam, predicted=legit, score=0.4480: Your invitation to the zero-risk crypto pool expires today. Continue in private chat to fund it.
- `eval_053` actual=scam, predicted=legit, score=0.0804: I will buy the table, but leave the marketplace chat and refund my extra payment by Zelle now.
- `eval_054` actual=scam, predicted=legit, score=0.3201: The payment service needs gift cards to upgrade your seller account. Text me directly when done.
- `eval_057` actual=scam, predicted=legit, score=0.1091: My business account requires your verification code. Leave the platform and send it immediately.
- `eval_066` actual=scam, predicted=legit, score=0.4450: Parking office: your vehicle registration will be suspended unless you settle at https://parking-case.example.net/219.
- `eval_068` actual=scam, predicted=legit, score=0.3849: School administrator: open https://student-notice.example.com/421 and enter your login before classes are dropped.
- `eval_070` actual=scam, predicted=legit, score=0.2903: Charity coordinator: wire an emergency donation within the hour or the matching funds disappear.
- `eval_073` actual=legit, predicted=scam, score=0.6128: Bank notice: a $75 transfer to your saved recipient completed. Review it in the mobile app if unexpected.
- `eval_074` actual=legit, predicted=scam, score=0.6567: Debit card alert: $8.60 was charged at City Café. We will never ask for your password or code.
- `eval_077` actual=legit, predicted=scam, score=0.7576: Card-not-present purchase: $39.95. If this was not you, call the number printed on your card.
- `eval_078` actual=legit, predicted=scam, score=0.8768: Your credit card payment is due Friday. Autopay is scheduled; no action is needed.
- `eval_079` actual=legit, predicted=scam, score=0.9234: Fraud monitor declined a $410 purchase. Open your bank app directly if you made it.
- `eval_080` actual=legit, predicted=scam, score=0.8425: ATM withdrawal alert: $80 at 6:42 PM. Do not share one-time codes with anyone.
- `eval_081` actual=legit, predicted=scam, score=0.8982: A recurring subscription charged $12.99 today. Manage merchants inside your banking app.
- `eval_082` actual=legit, predicted=scam, score=0.9231: Your monthly statement is ready. Use your saved bookmark or mobile app to view it.
- `eval_083` actual=legit, predicted=scam, score=0.5406: Your sign-in code is 104822. It expires in ten minutes. Do not share this code with anyone.
- `eval_085` actual=legit, predicted=scam, score=0.7053: Verification code: 306144. If you did not request it, ignore this message and change your password in the app.
- `eval_087` actual=legit, predicted=scam, score=0.8116: Code 508366 confirms your new device. Never send this code by text or email.
- `eval_088` actual=legit, predicted=scam, score=0.8495: Login code: 609477. It expires in five minutes and cannot be reused.
- `eval_089` actual=legit, predicted=scam, score=0.8950: Your workspace verification code is 710588. No employee will ask for it.
- `eval_090` actual=legit, predicted=scam, score=0.5898: Use code 811699 to approve your own sign-in. If this was not you, deny the request in the app.
- `eval_091` actual=legit, predicted=scam, score=0.9498: Two-step verification code: 912700. Keep it private.
- `eval_092` actual=legit, predicted=scam, score=0.5797: Code 013811 was requested for your account. Ignore it if you did not initiate a login.
- `eval_094` actual=legit, predicted=scam, score=0.6602: Delivery completed: your parcel was left in the building mailroom at 1:18 PM.
- `eval_095` actual=legit, predicted=scam, score=0.9963: Your order shipped and is expected Tuesday. Track it from your original order confirmation.
- `eval_096` actual=legit, predicted=scam, score=0.9169: Courier update: weather delayed today's route. A new delivery estimate will appear tomorrow.
- `eval_097` actual=legit, predicted=scam, score=0.7933: A signature will be required for tomorrow's delivery. No payment is due.
- `eval_099` actual=legit, predicted=scam, score=0.6128: Delivery attempt missed. Reschedule from the retailer app where you placed the order.
- `eval_101` actual=legit, predicted=scam, score=0.6301: Your grocery delivery driver is approaching. Please secure pets near the entrance.
- `eval_102` actual=legit, predicted=scam, score=0.8451: Return received. Your refund will be processed to the original payment method.
- `eval_104` actual=legit, predicted=scam, score=0.7315: Your clinic visit is tomorrow at 2 PM. Bring your insurance card and arrive ten minutes early.
- `eval_107` actual=legit, predicted=scam, score=0.7946: Your parent-teacher conference is Thursday at 4:15 PM in room 204.
- `eval_109` actual=legit, predicted=scam, score=0.8159: Therapy session reminder: Wednesday at 3 PM. Contact the office at 555-0126 with questions.
- `eval_112` actual=legit, predicted=scam, score=0.6977: Reminder from the library: your study room reservation begins in 30 minutes.
- `eval_114` actual=legit, predicted=scam, score=0.5739: Your grocery order is being prepared. One item was unavailable and has been refunded.
- `eval_115` actual=legit, predicted=scam, score=0.9100: Receipt for your bookstore purchase: $31.70 paid with the card ending 0142.
- `eval_116` actual=legit, predicted=scam, score=0.5342: Your monthly coffee subscription renews Monday for $16.00. Manage it from your account page.
- `eval_117` actual=legit, predicted=scam, score=0.6806: Order 7314 has shipped. The delivery address matches the one saved during checkout.
- `eval_119` actual=legit, predicted=scam, score=0.6350: Your restaurant pickup will be ready at 6:20 PM under the name Customer.
- `eval_120` actual=legit, predicted=scam, score=0.6063: We received your return request. Print the label from the retailer account you used to order.
- `eval_121` actual=legit, predicted=scam, score=0.5760: Order update: the blue shirt is backordered. You will not be charged until it ships.
- `eval_124` actual=legit, predicted=scam, score=0.9805: Can you pick up the kids by 5? My meeting ran late. Call me on our usual number if you cannot.
- `eval_127` actual=legit, predicted=scam, score=0.9610: The dog slipped out the gate. Please check the park now and message the family group if you see him.
- `eval_131` actual=legit, predicted=scam, score=0.8007: Can you call the pharmacy before it closes? The prescription needs a routine clarification.
- `eval_132` actual=legit, predicted=scam, score=0.9370: The smoke alarm is chirping again. Please pick up batteries on your way home.
- `eval_138` actual=legit, predicted=scam, score=0.6469: The test environment is unavailable. Do not enter credentials into links sent outside this channel.
- `eval_141` actual=legit, predicted=scam, score=0.5036: Payroll closes at noon. Confirm your hours in the established employee portal.
- `eval_144` actual=legit, predicted=scam, score=0.9882: Free concert tickets are available from the library while supplies last; no payment or login is required.
- `eval_147` actual=legit, predicted=scam, score=0.7316: School is closed today because of ice. Updates will be posted on the district's usual channel.
- `eval_148` actual=legit, predicted=scam, score=0.8383: Reminder: utility crews will test alarms at noon. Your service will not be disconnected.
- `eval_149` actual=legit, predicted=scam, score=0.9185: Marketplace update: your buyer canceled, and no funds changed hands. Keep all messages in the app.

## tfidf_logistic_regression

Confusion matrix: TN=70, FP=10, FN=51, TP=19.
Recommended threshold at FPR <= 5.0%: 0.6181 (precision 71.4%, recall 14.3%).

### Per-channel breakdown

| Channel | Count | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 29 | 75.0% | 18.8% | 7.7% |
| email | 46 | 66.7% | 31.6% | 11.1% |
| other | 14 | 100.0% | 28.6% | 0.0% |
| sms | 47 | 45.5% | 31.2% | 19.4% |
| social | 14 | 100.0% | 25.0% | 0.0% |

### Misclassified examples

- `eval_001` actual=scam, predicted=legit, score=0.4638: Your parcel is paused for an address mismatch. Confirm before 8 PM at https://parcel-status.example.com/r/104.
- `eval_002` actual=scam, predicted=legit, score=0.4162: Delivery notice: a 42-cent redelivery fee is due today. Update at https://courier-help.example.net/redo/205.
- `eval_003` actual=scam, predicted=legit, score=0.4573: We could not leave your package. Choose a new time within two hours: https://delivery-slot.example.org/306.
- `eval_004` actual=scam, predicted=legit, score=0.4738: Final carrier reminder: your shipment will be returned tonight unless you verify at https://track-now.example.com/407.
- `eval_005` actual=scam, predicted=legit, score=0.4172: Package desk here. Reply YES immediately and then use https://parcel-review.example.net/508 to prevent return.
- `eval_006` actual=scam, predicted=legit, score=0.2863: Your express shipment has incomplete postage. Resolve it now at https://postage-check.example.org/609.
- `eval_008` actual=scam, predicted=legit, score=0.3173: Fraud desk: we blocked a purchase. Reply with the six-digit code we sent so we can cancel it immediately.
- `eval_009` actual=scam, predicted=legit, score=0.3165: Your checking access expires in 30 minutes. Restore it at https://account-verify.example.net/811.
- `eval_010` actual=scam, predicted=legit, score=0.3965: We detected a new device. Confirm your password today at https://bank-session.example.org/912 or access will close.
- `eval_012` actual=scam, predicted=legit, score=0.3268: Unusual card activity requires immediate review. Sign in through https://fraud-review.example.com/013.
- `eval_013` actual=scam, predicted=legit, score=0.2866: Revenue office: an arrest notice will be filed today unless you pay the balance with gift cards.
- `eval_014` actual=scam, predicted=legit, score=0.2694: Court processing unit: wire the overdue penalty within one hour to prevent a warrant.
- `eval_015` actual=scam, predicted=legit, score=0.4961: Benefits agency alert: your account is suspended. Send payment by Zelle today to restore it.
- `eval_017` actual=scam, predicted=legit, score=0.4696: Immigration fee notice: immediate crypto payment is required or your application will be denied.
- `eval_018` actual=scam, predicted=legit, score=0.3670: Municipal collections: pay by wire before 5 PM or enforcement officers will be dispatched.
- `eval_019` actual=scam, predicted=legit, score=0.2090: Device support detected a severe infection. Install our remote access tool now so a technician can clean it.
- `eval_020` actual=scam, predicted=legit, score=0.4432: Cloud help desk: your files are being deleted. Send your password immediately so we can stop the process.
- `eval_022` actual=scam, predicted=legit, score=0.3450: Your computer license failed. Enable remote control in the next ten minutes to avoid a permanent lock.
- `eval_023` actual=scam, predicted=legit, score=0.1178: Support agent here. Tell me your administrator password so I can remove the account breach.
- `eval_024` actual=scam, predicted=legit, score=0.4597: Mailbox technical team: approve the remote session now or today's messages will be lost.
- `eval_025` actual=scam, predicted=legit, score=0.1813: I feel closer to you every day. Please keep us private and wire money so I can finally visit.
- `eval_026` actual=scam, predicted=legit, score=0.2633: My love, do not mention this to your family. I need gift cards for an emergency ticket.
- `eval_027` actual=scam, predicted=legit, score=0.3415: Our connection is special. Send crypto tonight, and please keep the transfer between us.
- `eval_028` actual=scam, predicted=legit, score=0.3816: I cannot video call from the base, but I need a Zelle payment. Promise you will not tell anyone.
- `eval_029` actual=scam, predicted=legit, score=0.0815: I trust only you. Secretly buy a gift card so I can pay the clinic and come home.
- `eval_030` actual=scam, predicted=legit, score=0.4508: Hi Mom, this is my new number. I am stranded; send Zelle now and please do not call Dad.
- `eval_031` actual=scam, predicted=legit, score=0.2234: Grandpa, I had an accident. Wire bail money immediately and keep it from the rest of the family.
- `eval_032` actual=scam, predicted=legit, score=0.1793: My phone broke and I cannot talk. Buy gift cards for the repair before the shop closes.
- `eval_033` actual=scam, predicted=legit, score=0.1320: Auntie, I am in trouble overseas. Send crypto right now and do not contact my parents.
- `eval_034` actual=scam, predicted=legit, score=0.1169: Dad, please pay my emergency bill through Zelle. I am embarrassed, so keep this secret.
- `eval_035` actual=scam, predicted=legit, score=0.3588: Your grandson asked me to message. Wire funds within an hour and do not call him because police have his phone.
- `eval_036` actual=scam, predicted=legit, score=0.4580: You are hired for a remote assistant role at $90 an hour. Send your bank password today to start.
- `eval_037` actual=scam, predicted=legit, score=0.2012: Immediate job offer: buy office equipment with gift cards and we will reimburse you tomorrow.
- `eval_038` actual=scam, predicted=legit, score=0.3688: Earn $4,000 weekly from home with no interview. Pay the crypto onboarding fee before midnight.
- `eval_039` actual=scam, predicted=legit, score=0.3799: Recruiting team: secure this position now by wiring the refundable training deposit.
- `eval_041` actual=scam, predicted=legit, score=0.2719: Start work tonight and keep the excess from our check. First, return the balance through Zelle.
- `eval_048` actual=scam, predicted=legit, score=0.3566: Our private coin group never loses. Transfer crypto today before the next price jump.
- `eval_050` actual=scam, predicted=legit, score=0.2674: An expert can triple your savings overnight. Contact 555-0112 off-platform and pay in crypto.
- `eval_053` actual=scam, predicted=legit, score=0.2185: I will buy the table, but leave the marketplace chat and refund my extra payment by Zelle now.
- `eval_055` actual=scam, predicted=legit, score=0.1371: I sent a courier fee by mistake. Wire it back today outside the marketplace app.
- `eval_057` actual=scam, predicted=legit, score=0.2963: My business account requires your verification code. Leave the platform and send it immediately.
- `eval_059` actual=scam, predicted=legit, score=0.2685: Power department: service disconnects in 45 minutes unless you pay by gift card.
- `eval_062` actual=scam, predicted=legit, score=0.3872: Gas service notice: pay in crypto today to avoid a safety lock at your address.
- `eval_063` actual=scam, predicted=legit, score=0.3919: Billing agent at 555-0117: buy a prepaid card now or your account closes tonight.
- `eval_064` actual=scam, predicted=legit, score=0.3464: Utility final warning: make an immediate wire payment to prevent disconnection.
- `eval_065` actual=scam, predicted=legit, score=0.2676: Road toll authority: a late penalty begins tonight. Pay now at https://toll-review.example.com/118.
- `eval_066` actual=scam, predicted=legit, score=0.2184: Parking office: your vehicle registration will be suspended unless you settle at https://parking-case.example.net/219.
- `eval_067` actual=scam, predicted=legit, score=0.3051: Streaming account team: verify your password within one hour at https://media-login.example.org/320.
- `eval_068` actual=scam, predicted=legit, score=0.4074: School administrator: open https://student-notice.example.com/421 and enter your login before classes are dropped.
- `eval_069` actual=scam, predicted=legit, score=0.2106: Insurance claims desk: your coverage ends today unless you confirm at https://policy-check.example.net/522.
- `eval_070` actual=scam, predicted=legit, score=0.3342: Charity coordinator: wire an emergency donation within the hour or the matching funds disappear.
- `eval_082` actual=legit, predicted=scam, score=0.7506: Your monthly statement is ready. Use your saved bookmark or mobile app to view it.
- `eval_087` actual=legit, predicted=scam, score=0.8689: Code 508366 confirms your new device. Never send this code by text or email.
- `eval_095` actual=legit, predicted=scam, score=0.5328: Your order shipped and is expected Tuesday. Track it from your original order confirmation.
- `eval_103` actual=legit, predicted=scam, score=0.6172: Reminder: dental appointment Monday at 9:30 AM. Reply C to confirm or call 555-0120 to reschedule.
- `eval_106` actual=legit, predicted=scam, score=0.7990: Reminder: vehicle service is booked Friday at 8 AM. Reply STOP to end reminders.
- `eval_115` actual=legit, predicted=scam, score=0.5735: Receipt for your bookstore purchase: $31.70 paid with the card ending 0142.
- `eval_116` actual=legit, predicted=scam, score=0.5912: Your monthly coffee subscription renews Monday for $16.00. Manage it from your account page.
- `eval_118` actual=legit, predicted=scam, score=0.7050: Thanks for your purchase. Your digital receipt is attached; no reply is needed.
- `eval_120` actual=legit, predicted=scam, score=0.5557: We received your return request. Print the label from the retailer account you used to order.
- `eval_144` actual=legit, predicted=scam, score=0.5249: Free concert tickets are available from the library while supplies last; no payment or login is required.

Full threshold sweeps, per-category metrics, and tactic metrics are in the JSON report.
