from noyaba.vm import VM
v=VM(); v.run('try:\n    9 / 0\nexcept CenterError as e:\n    view(e)\nx = 4\nview(x)\n')
print(v.output)
