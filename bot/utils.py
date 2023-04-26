import constants


def is_main_admin(user_id: int):
    return user_id in (constants.DEVELOPER_ID, constants.MAIN_ADMIN_ID)
