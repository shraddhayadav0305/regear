import requests
import re
import time

# simple check that the product detail page shows chat button and hides phone

def test_listing_detail():
    time.sleep(2)  # give server time to start
    url = 'http://localhost:5000/browse'
    try:
        # grab first listing id from browse page
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"browse page returned {resp.status_code}")
            return
        m = re.search(r'/listing/(\d+)', resp.text)
        if not m:
            print("no listing link found on browse page")
            return
        listing_id = m.group(1)
        detail_url = f'http://localhost:5000/listing/{listing_id}'
        resp = requests.get(detail_url)
        if resp.status_code != 200:
            print(f"detail page returned {resp.status_code}")
            return
        html = resp.text
        if 'Chat with seller' in html:
            print("✓ Chat button present")
        else:
            print("✗ Chat button missing")
        if 'Show number' in html:
            print("✓ Phone hidden behind Show number")
        else:
            print("✗ Phone visible directly")
        if 'fa-heart' in html:
            print("✓ Wishlist icon present")
        if 'fa-share-alt' in html:
            print("✓ Share icon present")
        # toggle wishlist for this listing
        resp_toggle = requests.get(f'http://localhost:5000/wishlist/toggle/{listing_id}')
        # after redirect the session cookie should be maintained automatically by requests
        wresp = requests.get('http://localhost:5000/api/wishlist')
        if wresp.status_code == 200 and str(listing_id) in wresp.text:
            print("✓ Wishlist API returns the item after toggle")
        else:
            print(f"✗ Wishlist API did not return item: {wresp.status_code} {wresp.text}")

        # follow link to seller profile
        m2 = re.search(r'/seller/(\d+)', html)
        if m2:
            seller_url = f"http://localhost:5000/seller/{m2.group(1)}"
            r2 = requests.get(seller_url)
            if r2.status_code == 200 and seller_url in r2.url:
                print("✓ Seller profile loads")
                if seller_url.split('/')[-1] in r2.text:
                    print("✓ Seller id included in profile page")
                if 'Items listed' in r2.text:
                    print("✓ Items listed section present")
                if '<i class="fas fa-comments"' in r2.text:
                    print("✓ Chat icon present on profile listings")
            else:
                print(f"✗ Seller profile failed ({r2.status_code})")
        else:
            print("✗ No seller link found on detail page")
    except Exception as e:
        print(f"error during test: {e}")

if __name__ == '__main__':
    test_listing_detail()
