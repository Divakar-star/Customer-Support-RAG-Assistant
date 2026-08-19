# Sample Document Brief — Acme Support Knowledge Base

Generate these 8 files yourself (e.g. with Gemini chat) and save each as **plain
Markdown** into `data/raw/`. Use the exact filenames below — the loader accepts
`.md`, `.txt`, and `.pdf`.

General instructions for whoever/whatever writes these:
- Use real Markdown headings (`#`, `##`) and `-` bullet lists.
- 300–600 words per document.
- Include the **specific facts** listed for each doc, word-for-word where a number
  or day-count is given — later evaluation questions will check these exact facts.
- Keep policy words like NOT / EXCEPT / WITHIN / AFTER / BEFORE / MUST / MAY / ONLY
  where they naturally occur — they carry legal meaning.
- Do not make the documents contradict each other in this round (a deliberate
  conflicting pair is a later exercise, not part of the MVP).
- No need for real PDFs — Markdown is fine for now.

---

## 1. `return_policy.md`
- Standard products may be returned **within 30 calendar days of delivery**.
- Items must be unused and returned with original packaging.
- Final-sale items, gift cards, and personalized products are NOT returnable.
- Holiday extension: items purchased Nov 1–Dec 24 may be returned until **Jan 31**.
- Return shipping is paid by the customer unless the item was defective.

## 2. `refund_policy.md`
- Refunds are normally processed within **5–10 business days** after inspection.
- Refunds are issued to the original payment method.
- Customers may request store credit instead, issued within 24 hours.
- If the item is used but functional, a **15% restocking fee** applies to partial refunds.

## 3. `shipping_policy.md`
- Standard shipping: 5–7 business days. Express: 2–3 business days. International: 10–20 business days.
- If a shipment is delayed more than **7 business days** past the estimate, the
  customer may request a $10 credit or a free express upgrade on their next order.
- Lost packages: customer must file a claim within 30 days of the expected delivery date.

## 4. `damaged_items_policy.md`
- Damaged items must be reported **within 7 days** of delivery.
- Customer must provide photo evidence of the damage.
- Customer's choice of full refund or replacement — no restocking fee applies.

## 5. `premium_support_plan.md`
- Premium Support Plan ("Plan A+") includes 24/7 phone support.
- Premium plan **does** include weekend support: Saturday–Sunday, 9am–6pm local time.
- The free/standard plan does **NOT** include weekend support — only Mon–Fri, 9am–6pm.
- Premium response-time SLA: 2 hours. Standard plan SLA: 24 hours.
- Mention full SLA terms are defined in "Section 9.3 of the Premium Support Agreement".

## 6. `account_security_guide.md`
- To reset a forgotten password, use the "Forgot Password" link on the login page;
  the reset email link is valid for **30 minutes**.
- After **5 failed login attempts**, the account is locked for 15 minutes.
- Two-factor authentication (2FA) can be enabled from account settings.
- Suspicious account activity must be reported to support within 24 hours.

## 7. `product_warranty.md`
- Standard warranty: **12 months** from purchase date, covers manufacturing defects only.
- Extended warranty: an additional 12 months, purchasable within 30 days of purchase.
- Warranty does NOT cover accidental damage, water damage, or unauthorized repairs.
- Warranty claims are processed within 10 business days.

## 8. `customer_service_faq.md`
Q&A style, 8–12 short question/answer pairs that summarize and cross-reference the
other documents, e.g.:
- "How do I start a return?" → points to the 30-day return window.
- "When will I get refunded?" → 5–10 business days after inspection.
- "Does support work on weekends?" → yes, on the Premium plan only.
- "What if my package is late?" → shipping delay policy.
- "I forgot my password, what do I do?" → account security guide steps.

---

Once these 8 files are in `data/raw/`, run:

```bash
python scripts/ingest_documents.py
```
