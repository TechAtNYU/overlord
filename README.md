Running overlord: `celery -A overlord worker -l info`
Running tasks: 

```python
from overlord import add

result = add.delay(1,1)
result.result
```
