# split-only-for-clean-abstraction

_Theme B: function-and-module-shape_

## conjoined self-state methods -> pure pipeline  ·  `python`  ·  synthetic

**Before**
```python
class CheckoutHandler:
    def handle(self, req):
        self._parse(req)    # sets self.cart
        self._price()       # reads self.cart, sets self.total
        self._charge()      # reads self.total, sets self.receipt
        return self.receipt

    def _parse(self, req):
        self.cart = [Item(**i) for i in req["items"]]

    def _price(self):
        self.total = sum(i.qty * i.unit_price for i in self.cart)

    def _charge(self):
        self.receipt = gateway.charge(self.total)
```

**After**
```python
def handle(req):
    cart = parse_cart(req)
    total = price(cart)
    return charge(total)

def parse_cart(req):
    return [Item(**i) for i in req["items"]]

def price(cart):
    return sum(i.qty * i.unit_price for i in cart)

def charge(total):
    return gateway.charge(total)
```

**Why:** Shows the right fix for conjoined helpers that communicate only through mutable self-state and a fixed call order: turn each into a pure value-in/value-out step so it's understandable without the parent. Guards the opposite pole - if these three genuinely co-mutated one buffer in lockstep and couldn't return values, you would inline them as a visible sequence rather than fake-extract.

---

## over-extracted passthrough helpers -> inline visible sequence  ·  `typescript`  ·  synthetic

**Before**
```typescript
class WebhookProcessor {
  private event!: StripeEvent;
  private order!: Order;

  process(raw: string): Order {
    this.decode(raw);
    this.loadOrder();
    this.markPaid();
    return this.order;
  }
  private decode(raw: string) { this.event = JSON.parse(raw); }
  private loadOrder() { this.order = db.orders.find(this.event.orderId); }
  private markPaid() { this.order.status = "paid"; db.orders.save(this.order); }
}
```

**After**
```typescript
function processWebhook(raw: string): Order {
  const event: StripeEvent = JSON.parse(raw);
  const order = db.orders.find(event.orderId);
  order.status = "paid";
  db.orders.save(order);
  return order;
}
```

**Why:** Demonstrates collapsing single-use trampolines that scatter a 4-line linear flow across methods threading state through fields, forcing the reader to flip back and forth. Guards the opposite pole - if decode had to verify a signature and parse (a non-trivial pure op reused elsewhere), keeping it as verifyAndParse(raw) would be the correct extraction.

---

## extract a warranted non-obvious pure operation  ·  `go`  ·  synthetic

**Before**
```go
func (c *Client) doWithRetry(req *http.Request) (*http.Response, error) {
    for attempt := 0; attempt < c.maxRetries; attempt++ {
        resp, err := c.http.Do(req)
        if err == nil && resp.StatusCode < 500 {
            return resp, nil
        }
        // exponential backoff with full jitter, capped at 30s
        capped := math.Min(float64(c.base)*math.Pow(2, float64(attempt)), float64(30*time.Second))
        time.Sleep(time.Duration(rand.Int63n(int64(capped))))
    }
    return nil, fmt.Errorf("exhausted %d retries", c.maxRetries)
}
```

**After**
```go
func (c *Client) doWithRetry(req *http.Request) (*http.Response, error) {
    for attempt := 0; attempt < c.maxRetries; attempt++ {
        resp, err := c.http.Do(req)
        if err == nil && resp.StatusCode < 500 {
            return resp, nil
        }
        time.Sleep(backoffWithJitter(attempt, c.base))
    }
    return nil, fmt.Errorf("exhausted %d retries", c.maxRetries)
}

// backoffWithJitter returns a randomized exponential delay capped at 30s.
func backoffWithJitter(attempt int, base time.Duration) time.Duration {
    capped := math.Min(float64(base)*math.Pow(2, float64(attempt)), float64(30*time.Second))
    return time.Duration(rand.Int63n(int64(capped)))
}
```

**Why:** Shows the apply side: the jitter math is a non-obvious pure operation (attempt in, duration out) whose revealing name replaces the what-comment and reads independently of the loop. Guards against over-applying - the retry loop with its mutable attempt counter and the one-line c.http.Do call stay inline as a visible sequence; only the pure block that earned a name is pulled out.

---
