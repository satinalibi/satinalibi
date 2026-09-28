# Satin Alibi — how this repo works

Satin Alibi (satinalibi.com) is a fashion and beauty blog that earns through affiliate links, fed by Pinterest.
Owner: Rabia. Claude writes the posts and pins; Rabia approves pins weekly before they go to Pinterest.

## Brand rules (non-negotiable)
- **Who it's for:** loud, forward, outspoken women who take up space, and the ones getting there. Never "quiet confidence", never "soft isn't weak". Loud on purpose.
- **Voice:** bold, direct, warm, a little wicked. Short sentences. Never apologetic. A feminism that lifts women up. Never tear other women down, never body-shame, never diet talk.
- **Look:** mature and editorial. Palette: bronze #A8703F, champagne #E8D3B0, ivory #F3ECE3, blush #EBC8C0, cherry #8E1622, ink #141012. Cormorant Garamond headlines, italic for the loud word.
- **Sensual, never explicit.** Pinterest removes or limits sexually suggestive content. Ads can't show nudity, implied nudity, or overtly sexual imagery. Show fabric and detail, not bodies. No lingerie-only framing: lace is worn *out*.
- **Honesty.** No invented first-person experiences ("I've used this for years"), no fake reviews or testimonials, no made-up product claims. Describe what a product is and why it fits the brand. Any factual claim must come from the product page or a reputable source. Prices say "at time of writing" on the site's disclosure page.
- **Images:** only Unsplash or Pexels photos (free for business use), or brand product images supplied through affiliate programs. Never Tumblr reposts. Never AI-generated people.

## Sections (also the Pinterest boards)
- `golden-hour`: body oils, self-tan, bronzer, gold jewelry, body chains, resort wear.
- `lace-and-pearls`: lace tops worn out, satin slips, embroidered tulle, feathers, pearls.
- `after-dark`: black lace, cherry lips, blazers over lace, fishnets, heels.
- `take-up-space`: no products and no affiliate links. Essays and quote pins on confidence, standards, self-respect, and being outspoken.

## Adding a post
Create `content/posts/<slug>.md`:

```yaml
---
title: "Body oils that make you *glow loud*"      # markdown allowed; the *italic* word shows in cherry
seo_title: "Best Shimmer Body Oils for a Bronzed Glow"   # optional, plain text, for Google/Pinterest
slug: shimmer-body-oils
section: golden-hour
date: 2026-09-28                  # goes live on this date (Toronto) via the daily build
status: published                 # or draft
dek: "One sentence under the title, in the brand voice."
hero: https://images.unsplash.com/photo-XXXXXXXXXXXXX   # base URL, no query string
hero_alt: "Describe the photo for screen readers"
hero_credit: "Name on Unsplash"
card_line: "Too much? Good."      # only for posts without a hero (shows as a cherry quote card)
products:                          # omit for take-up-space
  - brand: Brand
    name: Product name
    price: "$38 USD"
    retailer: Sephora
    url: https://www.sephora.com/...   # plain product URL; swapped for the affiliate link later
    note: "Two or three sentences on why it earns its place."
pins:
  - style: split | bleed | product | quote
    tone: ink | ivory | cherry | bronze   # split uses ink/ivory; quote uses any
    kicker: "Golden Hour"          # small label, optional
    line1: "Glow"
    line2: "loud."                 # the loud italic line, optional
    caption: "body oils that get you noticed"
    photo: https://images.unsplash.com/photo-...        # split and bleed
    photos: [url1, url2, url3]     # product style strip
    size: 180                      # optional headline px override
    pin_title: "Keyword-rich title under 100 characters"
    pin_description: "Natural, keyword-rich description under 500 characters, ending with a nudge to read the post."
    link: https://...              # optional: send the pin straight to a product instead of the post
---
Intro in markdown.

<!-- products -->

Outro in markdown: how to wear it, one strong closing line.
```

## Build
`python build.py` builds `dist/`; `python build.py --pins` also renders every pin to `dist/pins/<slug>-<n>.jpg` (1000×1500);
`--all` includes drafts and future posts for previews. `dist/pins/manifest.json` lists every pin with its title, description, board and link.
GitHub Actions builds on every push and daily at 6:15am Toronto, then publishes `dist/` to the `site` branch, which Cloudflare Pages serves.

## Pin mix and pace
About 3 in 4 pins are shopping pins; about 1 in 4 are Take Up Space quote pins. Around 5 pins a day at launch, building to 15+ a day by the end of month one.
Every pin needs Rabia's approval before it's scheduled (Pinterest requires the account owner to choose each pin).

## Approvals and auto-posting
1. After a build, pins appear in `dist/pins/manifest.json` with `status: pending`.
2. Rabia approves or skips each pin on her review page. Record her decisions with
   `python schedule_pins.py approve <ids...>` / `reject <ids...>`, then `python schedule_pins.py plan`
   to give approved pins publish dates (ramp: 5/day week 1, 8 week 2, 12 week 3, 15 after; boards interleaved).
   Never approve a pin on Rabia's behalf.
3. Decisions live in `content/pin-schedule.yml`. Commit and push.
4. The daily build writes one RSS feed per board at `/feeds/<section>.xml` containing approved pins whose
   publish date has arrived. Pinterest's "auto-publish from RSS" (connected once by Rabia, one feed per board)
   picks them up within 24 hours. Pins must link to satinalibi.com for this to work.
