from collections import defaultdict

from models import UserSetting, NotReadable, Operator, Permission, Filter

def merge_permissions(user_setting: UserSetting) -> UserSetting:
    merged_permissions = defaultdict(lambda: {"not_readables": set(), "permit_filter": Filter(), "permit_operators": set()})
    for permission in user_setting.setting.permissions:
        for item in permission.not_readables:
            merged_permissions[permission.index_name]["not_readables"].add(item.field)
        merged_permissions[permission.index_name]["permit_filter"].rules.append(permission.permit_filter)
        for operator in permission.permit_operators:
            merged_permissions[permission.index_name]["permit_operators"].add((operator.field, operator.metric))
    
    result_permissions = []
    for index_name, permission_data in merged_permissions.items():
        result_permissions.append(Permission(
            index_name = index_name,
            not_readables = [NotReadable(field = field) for field in permission_data["not_readables"]],
            permit_filter = permission_data["permit_filter"],
            permit_operators = [Operator(field = field, metric = metric) for field, metric in permission_data["permit_operators"]]
        ))
    user_setting.setting.permissions = result_permissions
    return user_setting
