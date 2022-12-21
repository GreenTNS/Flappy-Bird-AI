import torch

x = torch.randn(2, 3)
print(x)
y = torch.randn(2, 3)
print(y)
print(torch.add(x, y))

if torch.cuda.is_available():
    x = x.cuda()
print(x)
