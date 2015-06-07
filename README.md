Overlord now runs:

- Database backup on:
  - API server (MongoDB)
  - Wiki server (MySQL)
  - Business Development server (MySQL)

Running overlord: 

`cd overlord && make`

Running tasks: 

```python
from overlord import add

result = add.delay(1,1)
result.result
```

Long-running tasks vs one-off tasks

1. Long-running tasks don't need to be initiated by a person
2. One-off tasks can be initiated by a person through a HTTP request