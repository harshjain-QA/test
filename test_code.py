# from playwright.sync_api import sync_playwright
#
# def add_product_to_cart(page, product_name):
#     """Add a product to cart and close the mini cart"""
#     card = page.locator(".shelf-item").filter(has_text=product_name).first
#     card.locator("text=Add to cart").click()
#     print(f"✅ '{product_name}' added to cart")
#     close_cart = page.locator("//div[@class='float-cart__close-btn']")
#     close_cart.click()
#
#
# def test_playwright_checkout():
#     with sync_playwright() as p:
#         # Launch browser
#         browser = p.chromium.launch(headless=False, args=["--start-maximized"])
#         context = browser.new_context(no_viewport=True)
#         page = context.new_page()
#         page.set_default_timeout(30000)
#
#         # Open page and login
#         page.goto("https://bstackdemo.com/")
#         page.locator("//nav//span[text()='Sign In']").click()
#
#         # Select username
#         page.locator("//div[@id='username']").click()
#         page.locator("//div[@id='username']//div[contains(@class,'css-1n7v3ny-option') and text()='demouser']").click()
#
#         # Select password
#         page.locator("//div[@id='password']").click()
#         page.locator("//div[@id='password']//div[contains(@class,'css-1n7v3ny-option') and text()='testingisfun99']").click()
#
#         # Click login and wait for navigation
#         with page.expect_navigation():
#             page.locator("//button[@id='login-btn']").click()
#
#         # Wait for 'Sign Out' to confirm login
#         sign_out = page.locator("//nav//span[text()='Logout']")
#         sign_out.wait_for(state="visible", timeout=10000)
#         assert sign_out.count() == 1, "Login failed"
#         print("Login successful")
#
#         #  Add products to cart
#         add_product_to_cart(page, "iPhone 12 Mini")
#         add_product_to_cart(page, "Galaxy S20")
#
#         # Open cart and checkout
#         page.locator("//div[@class='float-cart']/span").click()
#         page.locator("//div[@class='buy-btn']").click()
#
#         # Validate total price
#         cart_items = page.locator("//section[@class='cart-section optimizedCheckout-orderSummary-cartSection'][1]/ul/li")
#         cart_items.first.wait_for(state="visible")
#         num_items = cart_items.count()
#         print(f"Number of items in cart: {num_items}")
#
#         total_calculated = 0.0
#         for i in range(num_items):
#             price_text = cart_items.nth(i).locator("xpath=./div/div[2]/div").inner_text().strip()
#             price = float(price_text.replace("$", "").strip())
#             print(f"Item {i+1} price: {price}")
#             total_calculated += price
#
#         total_text = page.locator("xpath=//div[@class='cart-priceItem optimizedCheckout-contentPrimary cart-priceItem--total']/span[2]/span").inner_text().strip()
#         total_displayed = float(total_text.replace("$", "").strip())
#         print(f"Calculated total: {total_calculated}, Displayed total: {total_displayed}")
#
#         assert total_calculated == total_displayed, f"Total mismatch! Calculated: {total_calculated}, Displayed: {total_displayed}"
#         print("Total amount matches the sum of items")
#
#         # Fill shipping details
#         first_name = page.locator("//input[@id='firstNameInput']")
#         last_name = page.locator("//input[@id='lastNameInput']")
#         address = page.locator("//input[@id='addressLine1Input']")
#         state = page.locator("//input[@id='provinceInput']")
#         postal_code = page.locator("//input[@id='postCodeInput']")
#
#         # Fill form
#         first_name.fill("Ram")
#         last_name.fill("Sharma")
#         address.fill("123 Maple Street")
#         state.fill("Springfield")
#         postal_code.fill("90210")
#
#         # 5Submit order
#         page.locator("//button").click()
#
#         # capture order number
#         order_number_capture = page.locator("//div[@class='checkout-form']/div[2]/strong")
#         order_number_capture.wait_for(state="visible")
#         order_number = order_number_capture.text_content()
#         print(f"✅ Your order number is: {order_number}")
#
#         page.wait_for_timeout(5000)
#
#         # Close browser
#         browser.close()
import pytest
from playwright.sync_api import sync_playwright, Page, expect
from pytest import fixture


# ---------------- Utility Functions ---------------- #

def login(page: Page):
    page.goto("https://bstackdemo.com/")
    page.locator("//nav//span[text()='Sign In']").click()

    page.locator("//div[@id='username']").click()
    page.locator("//div[contains(text(),'demouser')]").click()

    page.locator("//div[@id='password']").click()
    page.locator("//div[contains(text(),'testingisfun99')]").click()

    page.locator("//button[@id='login-btn']").click()

    expect(page.locator("//nav//span[text()='Logout']")).to_be_visible()


def add_product_to_cart(page: Page, product_name: str):
    card = page.locator(".shelf-item").filter(has_text=product_name).first
    card.locator("text=Add to cart").click()
    page.locator("//div[@class='float-cart__close-btn']").click()


# ---------------- Fixtures ---------------- #

@fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        yield context
        browser.close()


@fixture
def page(browser_context):
    page = browser_context.new_page()
    page.set_default_timeout(30000)
    yield page
    page.close()


@fixture
def cart_data(page):
    login(page)

    add_product_to_cart(page, "iPhone 12 Mini")
    add_product_to_cart(page, "Galaxy S20")

    page.locator("//div[@class='float-cart']/span").click()
    page.locator("//div[@class='buy-btn']").click()

    cart_items = page.locator(
        "//section[@class='cart-section optimizedCheckout-orderSummary-cartSection'][1]/ul/li"
    )
    cart_items.first.wait_for(state="visible")

    return cart_items


# ---------------- Tests ---------------- #

def test_login(page):
    login(page)
    print("✅ Login test passed")


def test_add_products(cart_data):
    expect(cart_data).to_have_count(2)
    print("✅ Products added to cart successfully")

# @pytest.mark.smoke
def test_total_calculation(cart_data, page):
    total_calculated = 0.0

    for i in range(cart_data.count()):
        price_text = cart_data.nth(i).locator("xpath=./div/div[2]/div").inner_text().strip()
        total_calculated += float(price_text.replace("$", "").strip())

    total_text = page.locator(
        "//div[contains(@class,'cart-priceItem--total')]//span[2]"
    ).inner_text().strip()

    total_displayed = float(total_text.replace("$", "").strip())

    assert round(total_calculated, 2) == round(total_displayed, 2), \
        "Total mismatch"
    print("✅ Total calculation matches")


def test_shipping_and_order(cart_data, page):
    page.locator("//input[@id='firstNameInput']").fill("Ram")
    page.locator("//input[@id='lastNameInput']").fill("Sharma")
    page.locator("//input[@id='addressLine1Input']").fill("123 Maple Street")
    page.locator("//input[@id='provinceInput']").fill("Springfield")
    page.locator("//input[@id='postCodeInput']").fill("90210")

    page.locator("//button[contains(text(),'Submit')]").click()

    order = page.locator("//div[@class='checkout-form']/div[2]/strong")
    expect(order).to_be_visible()

    print(f"✅ Order number: {order.text_content()}")


def test_empty_cart_checkout(page):
    login(page)

    page.locator("//div[@class='float-cart']/span").click()
    buy_button = page.locator("//div[@class='buy-btn']")

    assert buy_button.inner_text().strip() != "Check out"
    print("✅ Empty cart test passed")


def test_remove_item_from_cart(cart_data, page):
    page.go_back()

    page.locator("//div[@class='float-cart']/span").click()

    cart_items = page.locator("//div[@class='float-cart__shelf-container']//div[@class='shelf-item']")

    initial_count = cart_items.count()

    cart_items.first.locator(".shelf-item__del").click()

    expect(cart_items).to_have_count(initial_count - 1)
    print("✅ Item removed successfully")


def test_add_same_item_twice(page):
    login(page)

    add_product_to_cart(page, "iPhone 12 Mini")
    add_product_to_cart(page, "iPhone 12 Mini")

    page.locator("//div[@class='float-cart']/span").click()

    quantity_text = page.locator("//div[@class='shelf-item__details']/p[2]").inner_text()

    quantity = int(quantity_text.split(":")[-1].strip())

    assert quantity == 2
    print("✅ Quantity updated correctly")


def test_total_after_removal(cart_data, page):
    page.go_back()

    page.locator("//div[@class='float-cart']/span").click()

    cart_items = page.locator("//div[@class='float-cart__shelf-container']//div[@class='shelf-item']")

    cart_items.first.locator(".shelf-item__del").click()

    page.locator("//div[@class='buy-btn']").click()

    remaining_items = page.locator("//section[@class='cart-section optimizedCheckout-orderSummary-cartSection'][1]/ul/li")

    total_calculated = 0
    for i in range(remaining_items.count()):
        price = remaining_items.nth(i).locator("xpath=./div/div[2]/div").inner_text()
        total_calculated += float(price.replace("$", "").strip())

    total_displayed = float(page.locator("//div[contains(@class,'cart-priceItem--total')]//span[2]").inner_text().replace("$", "").strip())

    assert round(total_calculated, 2) == round(total_displayed, 2)
    print("✅ Total after removal correct")
    print("ok")