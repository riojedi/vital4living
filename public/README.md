# Vital4Living — Cloudflare Pages deployment

Static site, no build step. Deployed to **vital4living.com** via Cloudflare Pages.

## What's here

- `index.html` — multi-vertical home
- `snow/index.html` — snowsports vertical landing
- `snow/boots/boot-fit-engine.html` — the flagship Boot Fit Engine calculator
- `about/index.html` — author bio + editorial policy (E-E-A-T)
- `affiliate-disclosure/index.html` — affiliate disclosure
- `assets/css/style.css` — design system (alpine palette, Cabinet Grotesk + Satoshi)
- `assets/js/theme.js` — dark mode toggle
- `assets/js/boot-fit-engine.js` — the calculator logic
- `assets/img/logo.svg` — brand mark
- `robots.txt`, `sitemap.xml` — SEO

## Cloudflare Pages setup

1. Cloudflare dashboard → Workers & Pages → Create → Pages → Upload assets (or connect a Git repo).
2. Project name: `vital4living`. Production branch: `main`.
3. Build command: none. Output directory: `/` (root of this folder).
4. Custom domain: add `vital4living.com` and `www.vital4living.com` (DNS already on Cloudflare).
5. After first deploy, submit `sitemap.xml` in Google Search Console + Bing Webmaster.

## Path notes

All asset and internal links use **relative paths**, so the site works whether served from the domain root or a subpath preview.

## Calculator logic summary

- **Mondo size:** US men's + 18, US women's + 16.5, or foot length (cm) + 1.0 — rounded to nearest 0.5.
- **Last width band:** Narrow 92–98 / Medium 98–102 / Wide 102–106 / Extra-wide 106–112 mm.
- **Volume class:** last-width score + instep score → low / medium / high.
- **Flex index:** ability band (50–70 / 70–90 / 90–110 / 110–130) adjusted ±10 by body weight.
- **Brand fit:** general fit tendencies by volume class (Tecnica/Lange narrow; Salomon/Atomic/Nordica medium; Head/Dalbello/Fischer/K2 wide).

Educational only — does not set binding release values; defers to a certified bootfitter.
