from test.task import test_task

result_1 = test_task.delay(3)
result_2 = test_task.delay(5)

print(result_1.get())

print(result_2.get())
