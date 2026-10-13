"""Functional and accessibility checks; tooling is only needed for development."""
import argparse
import functools
import json
import os
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def load_images(page):
    for image in page.locator('img').all():
        image.scroll_into_view_if_needed()
    page.wait_for_function('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)')
    page.evaluate('window.scrollTo(0, 0)')


def no_overflow(page):
    return page.evaluate('document.documentElement.scrollWidth <= innerWidth')


def contrast(foreground, background):
    def luminance(color):
        channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return sum(c * w for c, w in zip(linear, [0.2126, 0.7152, 0.0722]))
    low, high = sorted([luminance(foreground), luminance(background)])
    return (high + 0.05) / (low + 0.05)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--axe', type=Path, required=True, help='Path to axe-core/axe.min.js')
    args = parser.parse_args()
    assert args.axe.is_file(), 'Install axe-core before running these checks.'
    results = []
    accessibility = []
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}'
    captures = ROOT / 'docs' / 'capturas'
    captures.mkdir(parents=True, exist_ok=True)

    def passed(name):
        results.append(name)
        print(f'PASS: {name}')

    try:
        with sync_playwright() as playwright:
            options = {'headless': True, 'args': ['--no-sandbox']}
            chromium = os.environ.get('PROYECTA_CHROMIUM', '/usr/bin/chromium')
            if Path(chromium).is_file():
                options['executable_path'] = chromium
            browser = playwright.chromium.launch(**options)
            errors, failures, external = [], [], []
            for width, height, label in [(390, 844, 'movil'), (768, 1024, 'tableta'), (1440, 1000, 'escritorio')]:
                page = browser.new_page(viewport={'width': width, 'height': height})
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('response', lambda response: failures.append(response.url) if response.status >= 400 else None)
                page.on('request', lambda request: external.append(request.url) if not request.url.startswith(url) else None)
                page.goto(url, wait_until='networkidle')
                load_images(page)
                assert no_overflow(page), f'Horizontal overflow at {width}px'
                assert page.locator('.project-card:visible').count() == 6
                page.add_script_tag(path=str(args.axe.resolve()))
                audit = page.evaluate("""async () => {
                    const result = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','best-practice']}});
                    return { violations: result.violations, incomplete: result.incomplete.map(i => i.id), passes: result.passes.length };
                }""")
                assert not audit['violations'], json.dumps(audit['violations'], ensure_ascii=False)
                accessibility.append({'width': width, **audit})
                page.screenshot(path=str(captures / f'{label}-{width}.png'), full_page=True)
                page.screenshot(path=f'/tmp/proyecta-viewport-{width}.png')
                passed(f'{width}px: images, layout and axe audit')
                page.close()
            assert not errors and not failures and not external, (errors, failures, external)
            passed('No JavaScript errors, failed requests or external resources')

            page = browser.new_page(viewport={'width': 390, 'height': 844})
            page.goto(url, wait_until='networkidle')
            assert page.locator('h1').count() == 1
            headings = page.locator('h1,h2,h3').evaluate_all('(hs) => hs.map(h => Number(h.tagName[1]))')
            assert all(current <= previous + 1 for previous, current in zip(headings, headings[1:]))
            assert page.locator('a[href^="#"]').evaluate_all('(links) => links.every(a => document.getElementById(a.hash.slice(1)))')
            assert page.locator('input,select').evaluate_all('(fields) => fields.every(f => f.labels.length > 0)')
            passed('Semantic heading hierarchy, anchor destinations and associated labels')

            page.keyboard.press('Tab')
            assert page.locator('.skip-link').evaluate('(e) => e === document.activeElement')
            assert page.locator('.skip-link').evaluate('(e) => getComputedStyle(e).outlineStyle === "solid"')
            page.keyboard.press('Enter')
            assert page.locator('#contenido').evaluate('(e) => e === document.activeElement')
            passed('Keyboard skip link and visible focus')

            menu = page.locator('.menu-toggle')
            menu.focus()
            page.keyboard.press('Enter')
            assert menu.get_attribute('aria-expanded') == 'true'
            page.keyboard.press('Tab')
            assert page.locator('nav a').first.evaluate('(e) => e === document.activeElement')
            page.keyboard.press('Escape')
            assert menu.get_attribute('aria-expanded') == 'false'
            assert menu.evaluate('(e) => e === document.activeElement')
            page.keyboard.press('Enter')
            page.keyboard.press('Tab')
            page.keyboard.press('Enter')
            assert menu.get_attribute('aria-expanded') == 'false'
            assert page.locator('#feria h2').evaluate('(e) => e === document.activeElement')
            page.set_viewport_size({'width': 1440, 'height': 1000})
            page.locator('nav').wait_for(state='visible')
            menu.wait_for(state='hidden')
            assert page.locator('nav').is_visible() and not menu.is_visible()
            page.set_viewport_size({'width': 390, 'height': 844})
            menu.wait_for(state='visible')
            page.locator('nav').wait_for(state='hidden')
            assert not page.locator('nav').is_visible() and menu.is_visible()
            passed('Keyboard menu, Escape, destination focus and breakpoint synchronization')

            for category in ['tecnologia', 'sostenibilidad', 'diseno', 'todos']:
                button = page.locator(f'[data-filter="{category}"]')
                button.focus()
                page.keyboard.press('Space')
                count = 6 if category == 'todos' else 2
                assert page.locator('.project-card:visible').count() == count
                assert button.get_attribute('aria-pressed') == 'true'
                assert page.locator('#project-count').inner_text().startswith(str(count))
                assert page.locator('[data-filter][aria-pressed="true"]').count() == 1
            passed('All project filters by keyboard, pressed states and live count')

            page.locator('button[type="submit"]').click()
            assert page.locator('[aria-invalid="true"]').count() == 4
            assert page.locator('#full-name').evaluate('(e) => e === document.activeElement')
            assert page.locator('.field-error:visible').count() == 4
            page.locator('#full-name').fill('   ')
            page.locator('#email').fill('correo-invalido')
            page.locator('button[type="submit"]').click()
            assert page.locator('#full-name').get_attribute('aria-invalid') == 'true'
            assert page.locator('#email').get_attribute('aria-invalid') == 'true'
            passed('Empty fields, whitespace name, invalid email and first-error focus')

            sent = []
            page.on('request', lambda request: sent.append(request.url))
            page.locator('#full-name').fill('Ana Estudiante')
            page.locator('#email').fill('ana@example.com')
            page.locator('#role').select_option('expositor')
            page.locator('#consent').check()
            page.locator('button[type="submit"]').focus()
            page.keyboard.press('Enter')
            assert 'Tus datos son válidos' in page.locator('#form-feedback').inner_text()
            assert page.locator('[aria-invalid="true"]').count() == 0
            assert page.locator('#full-name').input_value() == ''
            assert not sent and page.evaluate('localStorage.length + sessionStorage.length') == 0
            assert 'ana@example.com' not in page.url
            passed('Valid submission, accessible feedback, reset and no data transmission/storage')

            for width in [320, 640, 1024, 1280, 1920]:
                page.set_viewport_size({'width': width, 'height': 900})
                assert no_overflow(page), f'Overflow at {width}px'
            passed('No horizontal overflow at 320, 640, 1024, 1280 and 1920px')
            page.close()

            zoom = browser.new_page(viewport={'width': 720, 'height': 500}, device_scale_factor=2)
            zoom.goto(url, wait_until='networkidle')
            assert no_overflow(zoom)
            assert zoom.locator('.project-card').count() == 6
            passed('Reflow equivalent to 200% zoom on a 1440px display (720 CSS px, DPR 2)')
            zoom.close()

            text = browser.new_page(viewport={'width': 390, 'height': 844})
            text.goto(url, wait_until='networkidle')
            text.evaluate("""() => {
                const elements = [...document.querySelectorAll('body, body *')];
                const sizes = elements.map(e => parseFloat(getComputedStyle(e).fontSize));
                elements.forEach((e, i) => { e.style.fontSize = `${sizes[i] * 2}px`; });
            }""")
            assert no_overflow(text), 'Overflow with 200% text enlargement'
            text.screenshot(path='/tmp/proyecta-text-200.png', full_page=True)
            passed('200% text enlargement at 390px without horizontal overflow')
            text.close()

            plain = browser.new_page(java_script_enabled=False, viewport={'width': 390, 'height': 844})
            plain.goto(url, wait_until='networkidle')
            assert plain.locator('nav').is_visible()
            assert plain.locator('.project-card:visible').count() == 6
            assert plain.locator('#full-name').is_disabled()
            assert plain.locator('noscript').is_visible()
            passed('Without JavaScript: navigation and projects remain available, demo form disabled')
            plain.close()
            reduced = browser.new_page(reduced_motion='reduce')
            reduced.goto(url, wait_until='networkidle')
            assert reduced.evaluate('getComputedStyle(document.documentElement).scrollBehavior') == 'auto'
            passed('Reduced-motion preference disables smooth scrolling')
            reduced.close()
            browser.close()

        pairs = [('#172322','#f8f8f2'),('#52615f','#f8f8f2'),('#52615f','#eef0e9'),('#ffffff','#294ce4'),('#d8ed64','#172322'),('#d0dbd5','#172322'),('#b7c5bd','#172322'),('#a12626','#f8f8f2'),('#657265','#ffffff')]
        ratios = [{'foreground': fg, 'background': bg, 'ratio': round(contrast(fg, bg), 2)} for fg, bg in pairs]
        assert all(pair['ratio'] >= 4.5 for pair in ratios)
        passed('Nine primary text/background combinations meet 4.5:1 contrast')
        report = {'groups_passed':len(results),'checks':results,'axe':accessibility,'contrast':ratios,'screenshots':[f'{label}-{width}.png' for width,label in [(390,'movil'),(768,'tableta'),(1440,'escritorio')]]}
        (ROOT / 'docs' / 'resultados-pruebas.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(f'\n{len(results)} groups passed. Screenshots and results saved to docs/.')
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
