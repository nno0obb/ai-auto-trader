# ai-auto-trader

## Local

```
$ python3 main.py
```


## ETC

```
$ curl https://ifconfig.me
<IP>
```

## Links

* OpenAI Developer Platform :: [Manage - Usage](https://platform.openai.com/usage)
* Upbit :: [Open API 관리](https://upbit.com/mypage/open_api_management)

## DATA

### # buy(bid) --> wait --> cancel

```
# https://docs.upbit.com/kr/reference/주문하기
{
    'created_at': '2025-08-10T17:08:01+09:00',
    'executed_volume': '0',
    'locked': '5002.5',
    'market': 'KRW-DOGE',
    'ord_type': 'price',
    'paid_fee': '0',
    'prevented_locked': '0',
    'price': '5000',
    'remaining_fee': '2.5',
    'reserved_fee': '2.5',
    'side': 'bid',
    'state': 'wait',
    'trades_count': 0,
    'uuid': '9b314ca9-7356-423e-a2af-...'
}
```

```
# https://docs.upbit.com/kr/reference/개별-주문-조회
{
    'application_name': 'self_issued_open_api',
    'avg_price': '315.1575',
    'created_at': '2025-08-10T17:08:01+09:00',
    'executed_volume': '15.87301587',
    'is_cancel_and_newable': False,
    'locked': '0.000000950475',
    'market': 'KRW-DOGE',
    'ord_type': 'price',
    'paid_fee': '2.499999999525',
    'prevented_locked': '0',
    'price': '5000',
    'remaining_fee': '0.000000000475',
    'reserved_fee': '2.5',
    'side': 'bid',
    'state': 'cancel',
    'thirdparty': False,
    'trades_count': 1,
    'uuid': '9b314ca9-7356-423e-a2af-...'
}
```

### # sell(ask) --> wait --> done

```
# https://docs.upbit.com/kr/reference/주문하기
{
    'created_at': '2025-08-10T17:08:06+09:00',
    'executed_volume': '0',
    'locked': '81.90686236',
    'market': 'KRW-MOODENG',
    'ord_type': 'market',
    'paid_fee': '0',
    'prevented_locked': '0',
    'prevented_volume': '0',
    'remaining_fee': '0',
    'remaining_volume': '81.90686236',
    'reserved_fee': '0',
    'side': 'ask',
    'state': 'wait',
    'trades_count': 0,
    'uuid': '06dc00e2-5231-45a4-b02d-...',
    'volume': '81.90686236'
}
```

```
# https://docs.upbit.com/kr/reference/개별-주문-조회
{
    'application_name': 'self_issued_open_api',
    'avg_price': '235.882',
    'created_at': '2025-08-10T17:08:06+09:00',
    'executed_volume': '81.90686236',
    'is_cancel_and_newable': False,
    'locked': '0',
    'market': 'KRW-MOODENG',
    'ord_type': 'market',
    'paid_fee': '9.66500975848',
    'prevented_locked': '0',
    'prevented_volume': '0',
    'remaining_fee': '0',
    'remaining_volume': '0',
    'reserved_fee': '0',
    'side': 'ask',
    'state': 'done',
    'thirdparty': False,
    'trades_count': 1,
    'uuid': '06dc00e2-5231-45a4-b02d-...',
    'volume': '81.90686236'
}
```