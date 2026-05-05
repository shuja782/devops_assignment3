import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:5000"


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(3)
    return driver


class TodoAppTests(unittest.TestCase):

    def setUp(self):
        self.driver = get_driver()
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get(BASE_URL)
        while True:
            delete_buttons = self.driver.find_elements(By.CLASS_NAME, "btn-delete")
            if not delete_buttons:
                break
            btn = delete_buttons[0]
            btn.click()
            self.wait.until(EC.staleness_of(btn))

    def tearDown(self):
        self.driver.quit()

    def add_task(self, task):
        input_box = self.wait.until(
            EC.presence_of_element_located((By.ID, "todo-input"))
        )
        input_box.clear()
        input_box.send_keys(task)
        add_btn = self.driver.find_element(By.ID, "add-btn")
        add_btn.click()
        self.wait.until(EC.staleness_of(add_btn))

    def test_01_page_loads(self):
        self.driver.get(BASE_URL)
        self.assertIn("Todo", self.driver.title)

    def test_02_page_title(self):
        self.driver.get(BASE_URL)
        self.assertEqual(self.driver.title, "Todo App")

    def test_03_input_field_exists(self):
        self.driver.get(BASE_URL)
        self.assertTrue(self.driver.find_element(By.ID, "todo-input"))

    def test_04_add_button_exists(self):
        self.driver.get(BASE_URL)
        self.assertTrue(self.driver.find_element(By.ID, "add-btn"))

    def test_05_add_todo(self):
        self.driver.get(BASE_URL)
        self.add_task("Buy groceries")
        self.assertIn("Buy groceries", self.driver.page_source)

    def test_06_add_multiple_todos(self):
        self.driver.get(BASE_URL)
        tasks = ["Task Alpha", "Task Beta", "Task Gamma"]
        for t in tasks:
            self.add_task(t)
        page = self.driver.page_source
        for t in tasks:
            self.assertIn(t, page)

    def test_07_empty_input_no_add(self):
        self.driver.get(BASE_URL)
        before = len(self.driver.find_elements(By.CLASS_NAME, "todo-item"))
        self.driver.find_element(By.ID, "add-btn").click()
        after = len(self.driver.find_elements(By.CLASS_NAME, "todo-item"))
        self.assertEqual(before, after)

    def test_08_done_button_exists(self):
        self.driver.get(BASE_URL)
        self.add_task("Test Done Button")
        self.assertGreater(
            len(self.driver.find_elements(By.CLASS_NAME, "btn-toggle")), 0
        )

    def test_09_delete_button_exists(self):
        self.driver.get(BASE_URL)
        self.add_task("Test Delete Button")
        self.assertGreater(
            len(self.driver.find_elements(By.CLASS_NAME, "btn-delete")), 0
        )

    def test_10_toggle_todo_done(self):
        self.driver.get(BASE_URL)
        self.add_task("Toggle me")
        btn = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn-toggle"))
        )
        btn.click()
        self.wait.until(EC.staleness_of(btn))
        done_items = self.driver.find_elements(By.CSS_SELECTOR, "span.done")
        self.assertGreater(len(done_items), 0)

    def test_11_toggle_todo_undone(self):
        self.driver.get(BASE_URL)
        self.add_task("Toggle back")
        btn = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn-toggle"))
        )
        btn.click()
        self.wait.until(EC.staleness_of(btn))
        btn_undo = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn-toggle"))
        )
        btn_undo.click()
        self.wait.until(EC.staleness_of(btn_undo))
        done_items = self.driver.find_elements(By.CSS_SELECTOR, "span.done")
        self.assertEqual(len(done_items), 0)

    def test_12_delete_todo(self):
        self.driver.get(BASE_URL)
        task = "Delete this task 99999"
        self.add_task(task)
        self.assertIn(task, self.driver.page_source)
        delete_btn = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn-delete"))
        )
        delete_btn.click()
        self.wait.until(EC.staleness_of(delete_btn))
        self.assertNotIn(task, self.driver.page_source)

    def test_13_health_endpoint(self):
        self.driver.get(f"{BASE_URL}/health")
        self.assertIn("ok", self.driver.page_source)

    def test_14_form_exists(self):
        self.driver.get(BASE_URL)
        self.assertGreater(len(self.driver.find_elements(By.TAG_NAME, "form")), 0)

    def test_15_todo_list_container(self):
        self.driver.get(BASE_URL)
        self.add_task("Container check task")
        self.assertTrue(self.driver.find_element(By.CLASS_NAME, "todo-list"))


if __name__ == "__main__":
    unittest.main(verbosity=2)