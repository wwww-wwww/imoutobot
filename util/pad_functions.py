from textwrap import wrap

def get_all_roles(member):
    roles = []
    for v in member.roles:
        role = member.guild.roles.get(v).name.lower()
        roles.extend(get_role_variations(role))

    return roles

def get_role_variations(role):
    roles = []
    if ("(" in role) and (")" in role):
        roles.append(role[:role.find("(")])
        roles.append(role.partition('(')[-1].rpartition(')')[0])
    else:
        roles.extend(get_correct_inst(role))
    
    return roles

def get_correct_inst(instr):
    inst = []
    if any(item.lower() in instr.lower() for item in ["electric bass", "bass guitar", "gitah b"]):
        inst.extend(["electric bass", "bass guitar", "b. guitar"])
    elif ("drum" in instr.lower()):
        inst.extend(["drum"])
    elif any(item.lower() in instr.lower() for item in ["electric guitar", "e.guitar", "e. guitar", "gitah e"]):
        inst.extend(["electric guitar", "e.guitar", "e. guitar"])
    elif any(item.lower() in instr.lower() for item in ["acoustic guitar",  "gitah a"]):
        inst.extend(["acoustic guitar", "a.guitar", "a. guitar"])
    elif any(item.lower() in instr.lower() for item in ["classical guitar",  "gitah c"]):
        inst.extend(["classical guitar", "c.guitar", "c. guitar"])
    elif any(item.lower() in instr.lower() for item in ["bari sax"]):
        inst.extend(["baritone sax", "bari sax"])
    else:
        inst.append(instr.lower())
    return inst
    
def wrap_lines(str):
    lines = []
    for line in str.splitlines():
        lines.extend(wrap(line, 120) if line else [""])
    return lines
