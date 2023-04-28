# Concurrent API Access

## When Concurrency Matters

If the resources being exposed by the classes of the API can be queried and
changed 'quickly', then in most cases the `urest` library will sequence calls
without issue. Here 'quickly' means within the timeout excepted by both the
server an the client, which means a maximum of 30 second using the default
values.

Note, though, the some clients will timeout well-before this default: or may
respond by sending multiple requests, as they will assume some network failure.
Again, in most cases, this will not matter as the client will be expecting the
API to be _idempotent_: multiple class will achieve the same effect as a single
call.

In some cases, though, clients will need to be aware that multiple classes can
be made to classes _whilst the internal state is still changing_. Additionally,
in some cases we also need to break the normal HTTP assumption that calls to the
API are idempotent: this is especially likely for API calls that _set_, _update_
or _delete_ the internal state.

In all these cases we need to be aware of the potential for concurrent access, and design the API accordingly. Micropython has a number of primitives within the [`uasyncio` library](https://docs.micropython.org/en/latest/library/uasyncio.html#)
to handle concurrent access, and this _Background_ document will not cover them all. Nor we will deal with the theory of concurrent design: the following focuses on explaining the core issues, alongside possible resolutions.

## An Example of a API Class Allowing Concurrency

For this _Background_ we will focus on the design of the
[`PWMLED`][urest.examples.pwmled.PWMLED] class, and look in detail at the design
of two internal helper methods `_slow_on()` and `_slow_off()`. Like the
[`SimpleLED`][urest.examples.simpleled.SimpleLED] class
[`PWMLED`][urest.examples.pwmled.PWMLED] class assumes control of a single GPIO pin. However, unlike [`SimpleLED`][urest.examples.simpleled.SimpleLED], the
[`PWMLED`][urest.examples.pwmled.PWMLED] class uses PWM to raise the apparent
average voltage of the GPIO pin from a minimum (or a maximum) to a maximum
(or minimum) over a period of time. Connecting an LED to the GPIO output controlled by
[`PWMLED`][urest.examples.pwmled.PWMLED] should then result in the LED appearing
to slowly brighten (or dim).

The [`PWMLED`][urest.examples.pwmled.PWMLED] class relies on two internal methods
to achieve the necessar control. The first, `_slow_on()`, 'raises' the output
from the minimum to the maximum by altering the PWN duty cycle.

```python
async def _slow_on(self):
    self._duty = 0

    while self._duty < (65000):
        print(f"duty on: {self._duty}")

        self._duty += PWM_STEP
        self._gpio.duty_u16(self._duty)

        await asyncio.sleep_ms(1000)

    else:
        self._state_attributes["current"] = 1

    self._gpio.duty_u16(2 ** 16)
```

Whilst the converse method, `_slow_off`, 'lowers' the apparent output by again altering the PWN duty cycle. This time from a maximum value to a minimum.

```python
async def _slow_off(self):
    self._duty = 2 ** 16

    while self._duty > 6000:
        print(f"duty off: {self._duty}")

        self._duty -= PWM_STEP
        self._gpio.duty_u16(self._duty)

        await asyncio.sleep_ms(1000)

    else:
        self._state_attributes["current"] = 0

    self._duty = 0
```

The expectation is therefore that when a client connect to the API point, e.g.
`/green_led0`, setting the '`desired`' value of the noun to `1` will result
in the output gradually moving from a minimum to a maximum value.

```
Already connected!
IP:  10.0.30.225
SERVER: Started on 0.0.0.0:80
CLIENT URI : [10.0.30.129] PUT /green_led0 HTTP/1.1
CLIENT HEAD: [10.0.30.129] {'host': '10.0.30.225', 'accept': '*/*', 'content-type': 'application/json', 'user-agent': 'curl/7.81.0', 'content-length': '13'}
CLIENT BODY: [10.0.30.129] {'desired': 1}
duty on: 0
duty on: 6550
duty on: 13100
duty on: 19650
duty on: 26200
duty on: 32750
duty on: 39300
duty on: 45850
duty on: 52400
duty on: 58950
```

Likewise a call to '`/green_led0`' with the '`desired`' value as `0` should result
in the output gradually moving from the maximum to the minimum value.

```
CLIENT URI : [10.0.30.129] PUT /green_led0 HTTP/1.1
CLIENT HEAD: [10.0.30.129] {'host': '10.0.30.225', 'accept': '*/*', 'content-type': 'application/json', 'user-agent': 'curl/7.81.0', 'content-length': '13'}
CLIENT BODY: [10.0.30.129] {'desired': 0}
duty off: 65536
duty off: 58986
duty off: 52436
duty off: 45886
duty off: 39336
duty off: 32786
duty off: 26236
duty off: 19686
duty off: 13136
duty off: 6586
```

## Sequential Assumptions

Note that whilst the implication above is the that _same_ client is making both
calls, this is **not** explicitly defined by the
[`PWMLED`][urest.examples.pwmled.PWMLED] class. In designing the API classes
there is a natural tendency to think about the API calls as occurring one after
another from the same client. But this behaviour is _not_ guaranteed by the
network. And indeed for performance and other reasons we should assume exactly
the reverse: **any method can be called by any client at any time**. If this is
a problem, then the API class (or classes) need to untangle the requests
appropriately.

Nonetheless, in some cases the code of the methods above will appear to work.
For instance if we draw this interaction more clearly as a _sequence_ diagram
for the two clients we might get Figure 1.

![Example of Sequential API Access](/media/sd_async_set.svg)

**Figure 1: Example of 'Sequential' API Access**

Again, this behaviour is _not_ guaranteed by the API. But it will _appear_ to
work as 'Client A' makes the API call successfully; shortly followed by `Client
B' starting its call sequence. But what happen if 'Client B' makes its call
before the LED has fully turned on?

In that case the API _itself_ will work. But there will be clash at the
controlled resource as shown in the sequence diagram in Figure 2.

![Example of Concurrent API Access](/media/sd_async_set_conflict.svg)

**Figure 2: Resource Contention in the 'Sequential' API Access**

If the API does not block the call of the second client, then _both_ calls will
'succeed'. This will result in the controlled LED rapidly changing states as
`_slow_on()` and `_slow_off()` fight over the same resource. Logging the outcome
might look like the following.

```
duty off: 65536
duty on: 58986
duty off: 65536
duty on: 58986
duty off: 65536
duty on: 58986
duty off: 65536
duty on: 58986
duty off: 65536
duty on: 58986
duty off: 65536
duty on: 58986
```

## Approaches to Concurrent Access

Solving this issue can be done in one of two ways

1. We could _block_ the API call by 'Client B' until 'Client A' has finished. The HTTP protocol also has code for 'temporary conditions' in the `300` sequence; so we could issue a notification to 'Client B' to try again later.
2. We could _deferr_ the API call, allowing 'Client B' to 'succeed': but not actually changing anything until the call started by 'Client A' completes.

Both approaches have some downsides. By blocking the API we call put an
additional burden on the client. Now the client has to have some ability to
'remember' its own request, along with logic to either retry the request or
handle the requests failure. Arguably the client should already have this logic
anyway: but many clients in scripts or other simple use cases may just issue a
single `curl` request and move on.

Deferring the API call, though, is in some ways a little less honest. We are
accepting the API call, and even issuing a 'success' code back to the client:
but we have no way of knowing whether the call will _actually_ succeed. So we
can make the error handling logic of the API (and the client) by choosing to
defer the request.

For the [`PWMLED`][urest.examples.pwmled.PWMLED] class, we will decide that
'failure' isn't really an issue, so will choose to defer the request. The next
problem is how we do that.

## Using Locks for Concurrency

If we look at the code of the `set_state()` method of
[`PWMLED`][urest.examples.pwmled.PWMLED] being called by 'Client A' and 'Client B'  we see the following.

```python
loop = asyncio.get_event_loop()

self._state_attributes["desired"] = state_attributes["desired"]

if self._state_attributes["desired"] == 0:
    self._state_attributes["current"] = 1

    loop.create_task(self._slow_off())
else:
    self._state_attributes["current"] = 0

    loop.create_task(self._slow_on())
```

We can see here that the `_slow_on()` and `_slow_off()` methods are actually
being called by a co-routine within the main `uasyncio` event loop. So a natural
way to stop the calls to `_slow_on()` and `_slow_off()` is to look at how the
event loop might sequence the calls for us.

By default the event loop will just run the calls together, allowing both
`_slow_on` and `_slow_off` to control the same resource. What we actually want,
though, is to for the event loop to wait until either `_slow_on` or `_slow_off`
has completed: and only then schedule the co-routine.

The easiest way to sequence two `uasyncio` calls in this way is to the use the
[`Lock`](https://docs.micropython.org/en/latest/library/uasyncio.html#class-lock)
class. Only one co-routine can 'acquire' the lock at any one time: and only
the co-routine that has acquired the (same) lock will run. This is exactly the
behaviour we need.

So we can alter the `_slow_on()` method as follows. When we enter the method we
first attempt to acquire the lock. This will either succeed, allowing the method
call to continue: or it will stop the execution of the co-routine until the lock
has been released. The rest of the method can now proceed as before.

However we **must** release the lock before we finish. Otherwise all subsequent
calls using the same lock will block: including the next time `_slow_on()` is
called. Failing to release locks can therefore lead to some interesting bugs...

```python
async def _slow_on(self):

    # Wait for the GPIO lock if we need to
    await self._gpio_lock.acquire()

    # Increase the duty cycle from 0 to near the
    # maximum in steps lasting 1s. We will also
    # allow other co-routines to run whilst we
    # are waiting for the next step to take place
    self._duty = 0

    while self._duty < (65000):
        print(f"duty on: {self._duty}")

        self._duty += PWM_STEP
        self._gpio.duty_u16(self._duty)

        await asyncio.sleep_ms(1000)

    else:
        self._state_attributes["current"] = 1

    # Set the duty cycle to maximum before we leave,
    # and release the GPIO lock
    self._duty = 2 ** 16
    self._gpio.duty_u16(self._duty)

    self._gpio_lock.release()
```

Modifying the `_slow_off()` method in the same way should complete the modifications to both methods.

```python
async def _slow_off(self):

    # Wait for the GPIO lock if we need to
    await self._gpio_lock.acquire()

    # Decrease the duty cycle from the maximum to
    # near 0 in steps lasting 1s. We will also
    # allow other co-routines to run whilst we
    # are waiting for the next step to take place
    self._duty = 2 ** 16

    while self._duty > 6000:
        print(f"duty off: {self._duty}")

        self._duty -= PWM_STEP
        self._gpio.duty_u16(self._duty)

        await asyncio.sleep_ms(1000)

    else:
        self._state_attributes["current"] = 0

    # Set the duty cycle to 0 before we leave,
    # and release the GPIO lock
    self._duty = 0
    self._gpio.duty_u16(self._duty)

    self._gpio_lock.release()
```

The last thing we need to do is to create the lock itself. We must make sure
that every _instance_ of the class uses the _same_ lock. If `_slow_on()` and
`_slow_off()` use different locks, then again things will _appear_ to work: but
only for calls to the same method. The natural place for per instance entities
is in the constructor, so we also need to modify the `__init__` method to create
our lock

```python
self._gpio_lock = asyncio.Lock()
```

The full class code is available for [`PWMLED`][urest.examples.pwmled.PWMLED],
but that should complete the modifications we need. Now both 'Client A' and
'Client B' can call the API; both will see their calls 'succeed' immediately ---
but the actual change will be sequenced. Moreover, the sequence will be
determined by the (unknown) order of requests made by the clients, but in a
'first in, first out' order. If we need to sequence the clients themselves, that
is a different problem: but we can use the API to provide 'client locks' or
something similar.
