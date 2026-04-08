"""Master of Haggling - CLI bargaining game.

Game goal:
- You are the customer negotiating with a merchant.
- Reach a deal within 5 rounds to win.
"""

from __future__ import annotations

from dataclasses import dataclass
import random

MAX_ROUNDS = 5


@dataclass
class Character:
    reservation_price: int


@dataclass
class Product:
    name: str
    cost: int
    list_price: int


class Customer(Character):
    def __init__(self, budget: int, remaining_times: int = MAX_ROUNDS) -> None:
        super().__init__(reservation_price=budget)
        self.remaining_times = remaining_times
        self.low_bound = 1
        self.high_bound = budget

    def bid(self) -> int:
        while True:
            raw = input("请输入你的出价（整数）：").strip()
            try:
                offer = int(raw)
            except ValueError:
                print("⚠️ 输入无效，请输入整数。")
                continue

            if offer <= 0:
                print("⚠️ 出价必须大于 0。")
                continue
            if offer > self.reservation_price:
                print(f"⚠️ 你最多只能出到预算 {self.reservation_price}。")
                continue
            return offer

    def remind_remaining_times(self) -> str:
        return f"剩余出价次数：{self.remaining_times}"

    def update_bounds(self, offer: int, feedback: str) -> None:
        if feedback == "too_low":
            self.low_bound = max(self.low_bound, offer + 1)
        elif feedback == "too_high":
            self.high_bound = min(self.high_bound, offer - 1)

        if self.low_bound > self.high_bound:
            self.low_bound, self.high_bound = self.high_bound, self.low_bound

    def get_suggested_price(self) -> int:
        return (self.low_bound + self.high_bound) // 2


class Merchant(Character):
    def __init__(self, floor_price: int) -> None:
        super().__init__(reservation_price=floor_price)

    def evaluate_offer(self, offer: int, customer_budget: int) -> tuple[bool, str]:
        if offer >= self.reservation_price:
            return True, "accepted"

        gap = self.reservation_price - offer
        if gap <= max(2, self.reservation_price // 20):
            return False, "close"

        if offer > customer_budget:
            return False, "too_high"
        return False, "too_low"


class HagglingGame:
    def __init__(self) -> None:
        self.product = self._random_product()
        customer_budget = random.randint(
            int(self.product.list_price * 0.75),
            int(self.product.list_price * 1.20),
        )
        merchant_floor = random.randint(
            int(self.product.cost * 1.10),
            int(self.product.list_price * 0.95),
        )
        customer_budget = max(customer_budget, merchant_floor)

        self.customer = Customer(budget=customer_budget)
        self.merchant = Merchant(floor_price=merchant_floor)

    @staticmethod
    def _random_product() -> Product:
        products = [
            Product("丝绸围巾", cost=80, list_price=150),
            Product("手工木雕", cost=120, list_price=220),
            Product("铜制茶壶", cost=95, list_price=180),
            Product("香料礼盒", cost=60, list_price=130),
            Product("皮革腰带", cost=70, list_price=140),
        ]
        return random.choice(products)

    def run(self) -> None:
        print("\n🎮 欢迎来到 Master of Haggling！")
        print(f"今日商品：{self.product.name}")
        print(f"商家标价：{self.product.list_price}")
        print(f"你的预算上限：{self.customer.reservation_price}\n")

        for round_no in range(1, MAX_ROUNDS + 1):
            print(f"--- 第 {round_no} 轮 ---")
            print(self.customer.remind_remaining_times())
            suggested = self.customer.get_suggested_price()
            print(f"💡 建议试探价：{suggested}")

            offer = self.customer.bid()
            accepted, feedback = self.merchant.evaluate_offer(
                offer, self.customer.reservation_price
            )
            self.customer.remaining_times -= 1

            if accepted:
                print(f"✅ 成交！你以 {offer} 买下了 {self.product.name}。")
                return

            if feedback == "close":
                print("🤝 商人：这个价格很接近了，再加一点！")
                self.customer.update_bounds(offer, "too_low")
            elif feedback == "too_low":
                print("📈 商人：太低了，再高一点。")
                self.customer.update_bounds(offer, "too_low")
            else:
                print("📉 商人：这个价格不合理，请重新考虑。")
                self.customer.update_bounds(offer, "too_high")

            if self.customer.remaining_times == 0:
                break
            print()

        print("\n❌ 5轮内未达成交易，议价失败。")
        print(f"商家心理底价约为：{self.merchant.reservation_price}")


if __name__ == "__main__":
    HagglingGame().run()
