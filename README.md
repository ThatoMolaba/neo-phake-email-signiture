# Neo Phake: Email Signature

A compact, table-based HTML email signature for Neo Phake. It uses a charcoal-on-white base, muted gold detailing, monospaced micro-labels and a restrained WhatsApp call to action. It is built for Gmail, Outlook and Apple Mail.

| Desktop | Phone (stacks automatically) |
|---|---|
| ![Desktop preview](preview/light.png) | ![Mobile preview](preview/mobile.png) |

Simulated dark mode (forced colour inversion, as in Outlook and the Gmail apps):

![Dark-mode preview](preview/dark.png)

## Files

| File | Purpose |
|---|---|
| `signature.html` | **Copy-ready signature** built from `config.json` (sample contact values until you replace them) |
| `signature.template.html` | Same signature with every variable as a `{{PLACEHOLDER}}` |
| `config.json` | Neo's details. Edit this file, then rebuild |
| `build.py` | Fills the template, checks number formats, and writes `signature.html` + `preview/signature.html` |
| `assets/neo-phake-portrait.png` | 192×192 round portrait with a gold ring (shown at 84×84 for retina sharpness) |
| `assets/neo-phake-portrait-square.jpg` | Square fallback portrait (7 KB) if you prefer a lighter file |
| `preview/` | Local preview HTML and rendered screenshots |

## Design notes

- **Hierarchy:** the name is set in light + bold weights at 21px. The title is in small gold capitals with tracking. The company is in a softer grey. Contact rows sit under single-letter monospaced labels (`M` `E` `W`), which give a quiet technical feel.
- **Geometry:** a 1px hairline divider has a short gold "node" at the top. A gold baseline segment runs into a warm-grey hairline. These are the only decorative elements, and both are built from table cells, so no images are used.
- **WhatsApp:** an outlined green pill reads `● Chat on WhatsApp →`. It is drawn with a cell border, so it survives Outlook and keeps working if a client strips colours.
- **Responsive without media queries:** the identity and contact blocks are two `align="left"` tables. They sit side by side up to the 580px max width and stack on phones.
- **Dark mode:** the signature uses no background colours, so clients that invert colours keep the text readable. The gold and green are mid-tones that read on both light and dark backgrounds.

## Placeholders

| Placeholder | Current value | Notes |
|---|---|---|
| `{{FIRST_NAME}}` / `{{LAST_NAME}}` / `{{FULL_NAME}}` | Neo / Phake / Neo Phake | |
| `{{JOB_TITLE}}` | Founder & Principal Consultant | **SAMPLE: confirm** |
| `{{COMPANY_NAME}}` | Phake Advisory | **SAMPLE: confirm** |
| `{{PHONE_DISPLAY}}` | +27 82 000 0000 | **SAMPLE**: how the number is shown |
| `{{PHONE_E164}}` | +27820000000 | **SAMPLE**: used in `tel:`; `+27`, no spaces, no leading 0 |
| `{{WHATSAPP_NUMBER}}` | 27820000000 | **SAMPLE**: used in `https://wa.me/…`; no `+`, spaces or leading 0 |
| `{{EMAIL}}` | neo@phakeadvisory.co.za | **SAMPLE** |
| `{{WEBSITE_URL}}` / `{{WEBSITE_DISPLAY}}` | https://www.phakeadvisory.co.za / phakeadvisory.co.za | **SAMPLE** |
| `{{LOCATION}}` | Johannesburg, ZA | **SAMPLE** |
| `{{TAGLINE}}` | Strategy · Technology · Growth | **SAMPLE**: or remove the last row |
| `{{PHOTO_URL}}` | GitHub raw URL of `assets/neo-phake-portrait.png` | Must be a public **https** URL (see below) |

**Converting a South African number:** `082 123 4567` becomes `+27821234567` for the phone field and `27821234567` for WhatsApp.

### Still needed from Neo
1. Exact job title and company or brand name.
2. Mobile number, which is also used for WhatsApp unless a separate business number is preferred.
3. Email address and website.
4. A company logo, if one exists. Without one, the text-based brand treatment (gold title and grey company line) stands in.
5. Where to host the portrait. The default GitHub raw URL only works while this repository is **public**. A company website, CDN or Google Drive public link is more permanent.

## Rebuild after editing

```bash
python3 build.py
```

The script warns you if the WhatsApp or phone number is not in South African international format.

## Installing

Always copy the **rendered** signature, not the source code. Open `signature.html` in Chrome, Safari or Edge, press **Ctrl/Cmd + A**, then **Ctrl/Cmd + C**.

### Gmail (web)
1. Open the gear icon, then **See all settings → General → Signature → Create new**. Name it "Neo Phake".
2. Click in the editor and paste with **Ctrl/Cmd + V**.
3. Under **Signature defaults**, choose it for new emails and for replies and forwards.
4. Optional: tick *Insert signature before quoted text*.
5. Click **Save Changes** at the bottom of the page.
6. If the portrait doesn't appear, the image URL is not publicly reachable. Host it elsewhere, rebuild, and paste again.

The Gmail mobile apps use the web signature only when the mobile signature setting is turned off.

### Outlook (new Outlook for Windows / Outlook on the web)
1. Go to **Settings → Accounts → Signatures → + New signature** and name it.
2. Paste into the editor.
3. Set it as the default for new messages and for replies and forwards, then click **Save**.

### Outlook (classic desktop for Windows)
1. Go to **File → Options → Mail → Signatures… → New**.
2. Paste into the edit box. Outlook keeps the table layout and borders.
3. Choose defaults for new messages and replies, then click **OK**.
4. Alternative: save `signature.html` as `%APPDATA%\Microsoft\Signatures\Neo Phake.htm`.

### Outlook for Mac
Go to **Outlook → Settings → Signatures → +**, paste, then set the defaults.

### Apple Mail (macOS)
1. Go to **Mail → Settings → Signatures**, select the account, and click **+**.
2. **Untick "Always match my default message font"**. If this stays ticked, the typography is overwritten.
3. Paste the copied signature into the right-hand pane and select it as the account's default.
4. If the image breaks, quit Mail, open `~/Library/Mail/V10/MailData/Signatures/` (V9 or V11 on other versions), edit the newest `.mailsignature` file, replace the body after the header lines with the contents of `signature.html`, save it, and lock the file (**Get Info → Locked**).

### iPhone Mail
iOS only stores plain or lightly styled signatures. Email the signature to yourself from desktop, copy it from the received message, and paste it into **Settings → Apps → Mail → Signature**. Shake to undo if iOS strips the formatting.

## Testing checklist

Send a test email to a Gmail address and an Outlook address, then check each item on both a desktop and a phone.

- [ ] **WhatsApp:** tap *Chat on WhatsApp →*. WhatsApp (or WhatsApp Web) opens a chat with **Neo's number** (not 27820000000).
- [ ] **WhatsApp URL:** hover over the link. It reads exactly `https://wa.me/27XXXXXXXXX`, with no `+`, spaces or leading 0.
- [ ] **Phone:** on a phone, tapping the number offers to call `+27…`. On desktop it offers FaceTime, Teams or Skype.
- [ ] **Email:** clicking the address opens a new message addressed to Neo.
- [ ] **Website:** the link opens the correct site over **https**, and so does the portrait, which also links to the site.
- [ ] **Image:** the portrait loads for an external recipient with images enabled. With images blocked, the alt text "Neo Phake, Founder & Principal Consultant" shows instead.
- [ ] **Dark mode:** the name and contact details stay readable in Gmail (iOS/Android), Outlook and Apple Mail in dark mode.
- [ ] **Layout:** the signature sits side by side on desktop and stacks neatly on a phone, with no horizontal scrolling.
- [ ] **Replies:** the signature appears on replies and forwards, if enabled.
