# Satin Alibi — how this repo works

Satin Alibi (satinalibi.com) is a fashion and beauty blog that earns through affiliate links, fed by Pinterest.
Owner: Rabia. Claude writes the posts and pins; Rabia approves pins weekly before they go to Pinterest.

## Brand rules (non-negotiable)
- **Who it's for:** loud, forward, outspoken women who take up space, and the ones getting there. Never "quiet confidence", never "soft isn't weak". Loud on purpose.
- **Voice:** bold, direct, warm, a little wicked. Short sentences. Never apologetic. A feminism that lifts women up. Never tear other women down, never body-shame, never diet talk.
- **Look (v2, 28 Sep 2026):** capture the *essence* of Rabia's SIREN Tumblr images: photo-first, cinematic film stills with subtitles, intimate close-ups (lips, cherries, lace, pearls, gold on skin, satin folds), warm film grain, scrapbook collages. Mature and editorial, never cartoonish, never flat blocks of colour. Red is an accent, not a background.
  Paper #F3EDE4, ink #15100E, cherry #9E1B25 (accents only), gold #B08445, blush #E9CFC6, night #0D0A09.
  Fonts: Instrument Serif (headlines, italic for the loud word), Instrument Sans (body, subtitles), Courier Prime (small caps labels), Homemade Apple (handwritten notes, sparingly).
  Pinterest Predicts 2026 trends that fit: Vamp Romantic (After Dark), Glamoratti (Golden Hour).
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
collage: [url1, url2, url3]        # optional; defaults to hero + pin photos (post header mood board)
note: "glow loud"                  # optional handwritten note; defaults to the section note
products:                          # omit for take-up-space
  - brand: Brand
    name: Product name
    price: "$38 USD"
    retailer: Sephora
    url: https://www.sephora.com/...   # plain product URL; swapped for the affiliate link later
    note: "Two or three sentences on why it earns its place."
pins:                              # five styles, all photo-led; 4–5 pins per post, mix styles
  - style: cover       # magazine cover: photo, huge title, 3 mono cover lines
    photo: URL
    line1: "Glow"
    line2: "loud."                 # italic second line
    kicker: "The glow issue"
    lines: ["7 shimmer body oils", "from $14", "one splurge"]
  - style: moodboard   # scrapbook: 4 taped photos on paper, big title, handwritten note
    photos: [URL, URL, URL, URL]
    line1: "Liquid"
    line2: "gold."
    note: "catch the light"
    caption: "shimmer oils, mostly under $50"
  - style: still       # one film still with a subtitle, title underneath
    photo: URL
    sub: "Glow like it's on purpose."   # original line, never a real film quote
    line1: "Body oils that"
    line2: "glow loud"
    caption: "golden hour"
  - style: edit        # shoppable 2x2 grid with numbered labels (swap to product images once affiliate images exist)
    photos: [URL, URL, URL, URL]
    labels: ["01 · the dry oil", "02 · the gel oil", "03 · the shimmer", "04 · the splurge"]
    line1: "Shimmer"
    line2: "under $50."
  - style: frames      # 2–3 stacked stills, the subtitle sentence carries across frames
    photos: [URL, URL]
    subs: ["Where are you going?", "Somewhere they'll see me."]
    bw: true           # optional black-and-white (use for take-up-space)
  # every pin also takes: pin_title (<100 chars, keyword-rich), pin_description (<500 chars),
  # size (headline px override), sub_size, sub_color: yellow, link (straight to a product)
---
Intro in markdown.

<!-- products -->

Outro in markdown: how to wear it, one strong closing line.
```

## Photos
- Never put big titles over a face or body on pins. Cover pins keep the title in a cream band above the photo (changed 28 Sep 2026 after Rabia flagged covered faces); subtitles on stills stay small and low.
- Rabia disliked (don't reuse): the woman in the white sun hat with pearls (photo-1613315986155), the red-dress-at-window header (photo-1681308838635), the dark yellow-satin street header (photo-1571887747018, "too dark") and pearls draped across a face (photo-1585409351049, "creepy"). Also avoid avant-garde/odd faces. She likes bright, warm, bronzed, satin, 70s film colour.
- Home header (28 Sep 2026, after several rounds): magazine masthead. "No apologies. *No alibis.*" on one line in Playfair Display ExtraBold (self-hosted, her pick), photo full width below (portrait crop on phones via <picture>). Photo: green satin dress, red gloves, apple (photo-1653152707179). Small top-right line: "Satin, gold and a little trouble." (her pick). She disliked "Bite first. Explain never." and the old bracketed subtitle. She wants bold, big lettering and little empty space.
- Lace & Pearls must feel couture: runway gowns, corsetry, opera gloves, pearls on skin, lace in dramatic light. No doilies or tablecloth lace.
- Home header: `hero`, `hero_alt`, `hero_sub` in site.yml. A URL can carry its own crop (`?crop=top`); `hero_flip: true` mirrors it and `hero_pos` sets the object-position (check phone width).

## Build
`python build.py` builds `dist/`; `python build.py --pins` also renders every pin to `dist/pins/<slug>-<n>.jpg` (1000×1500);
`--all` includes drafts and future posts for previews. `dist/pins/manifest.json` lists every pin with its title, description, board and link.
GitHub Actions builds on every push and daily at 6:15am Toronto, then publishes `dist/` to the `site` branch, which Cloudflare Pages serves.

## Pin mix and pace
About 3 in 4 pins are shopping pins; about 1 in 4 are Take Up Space film-still pins (black-and-white stills or frames with subtitles). Around 5 pins a day at launch, building to 15+ a day by the end of month one.
Every pin needs Rabia's approval before it's scheduled (Pinterest requires the account owner to choose each pin).

## Approvals and auto-posting
1. After a build, pins appear in `dist/pins/manifest.json` with `status: pending`.
2. Rabia approves or skips each pin on her review page. Record her decisions with
   `python schedule_pins.py approve <ids...>` / `reject <ids...>`, then `python schedule_pins.py plan`
   to give approved pins publish dates (ramp: 5/day week 1, 8 week 2, 12 week 3, 15 after; boards and posts interleaved).
   `plan --reshuffle` re-plans every pin that hasn't gone out yet (use it after adding a batch so posts stay spread out).
   Never approve a pin on Rabia's behalf.
3. Decisions live in `content/pin-schedule.yml`. Commit and push.
4. The daily build writes one RSS feed per board at `/feeds/<section>.xml` containing approved pins whose
   publish date has arrived. Pinterest's "auto-publish from RSS" (connected once by Rabia, one feed per board)
   picks them up within 24 hours. Pins must link to satinalibi.com for this to work.

## Rabia's pin review page
Review page (Claude artifact): https://claude.ai/artifact/329Lfq6xP8SXf1TFza4wxW
Her taps are saved in the page's database, collection `decisions`, one document per pin id: `{status: "approved"|"skipped", at}`.
To sync: read that collection (ArtifactData list), run `schedule_pins.py approve` / `reject` for her choices, then `plan`, commit and push.
To add a new batch: after the site branch has the new pin JPGs, pull them with `git archive origin/site pins | tar -x -C scratch/live`,
run `python tools/review_page.py scratch/review.html --pending --batch "Third batch"` (only pins with no decision yet in pin-schedule.yml),
and republish to the same URL. If a pin she already approved gets new photos, don't approve it: leave it out of pin-schedule.yml,
delete its old doc from `decisions`, and put it in the next batch.
Batch 2 (28 Sep 2026): the new couture Lace & Pearls post plus 4 re-photographed pins (lace-tops-to-wear-out-2/4/5, gold-and-pearls-5).
