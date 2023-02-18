from glassdoor import db


IS_DESTROYED = "is_destroyed"


def find(model, params=None, session=None):
    params, session = ensure_args(params, session)

    return session.query(model).filter_by(**params).first()


def where(model, params=None, session=None, unscoped=False):
    params, session = ensure_args(params, session)
    exact_params = {}
    list_params = {}

    for k, v in params.items():
        if type(v).__name__ in ["list", "tuple"]:
            list_params[k] = tuple(v)
        else:
            exact_params[k] = v

    if (
        hasattr(model, IS_DESTROYED)
        and not exact_params.get(IS_DESTROYED)
        and not unscoped
    ):
        exact_params[IS_DESTROYED] = False

    query = session.query(model).filter_by(**exact_params)

    for k, v in list_params.items():
        query = query.filter(getattr(model, k).in_(v))

    return query.all()


def find_or_initialize_by(
    model, find_by_params=None, update_params=None, session=None, unscoped=False
):
    find_by_params, session = ensure_args(find_by_params, session)
    record = find(model, find_by_params.copy(), session)
    update_params = update_params or {}

    if not record:
        is_new = True
        find_by_params.update(update_params)  # merge the 2 dicts
        record = insert(model, find_by_params, session)
    else:
        is_new = False
        record = update(record, update_params, session)

    return record, is_new


def update(model_instance, params=None, session=None):
    params, session = ensure_args(params, session)

    try:
        [setattr(model_instance, k, v) for k, v in params.items()]
    except Exception as e:
        raise Exception(
            "Error updating {} with params: {} with error: {}".format(
                type(model_instance).__name__, params, e.message
            )
        )

    return model_instance


def insert(model, params=None, session=None):
    params, session = ensure_args(params, session)
    model_instance = model(params)

    try:
        session.add(model_instance)
    except Exception as e:
        raise Exception(
            "Error creating {} with params: {} with error: {}".format(
                model, params, e.message
            )
        )

    return model_instance


def delete(model, params=None, session=None):
    params, session = ensure_args(params, session)
    result = find(model, params, session)

    if result:
        try:
            session.delete(result)
        except Exception as e:
            raise Exception(
                "Error deleting {} with params: {} with error: {}".format(
                    model, params, e.message
                )
            )

        return True
    else:
        return False


def delete_instance(model_instance, session=None):
    session = session or create_session()

    try:
        session.delete(model_instance)
    except Exception as e:
        raise Exception(
            "Error deleting {} with error: {}".format(
                type(model_instance).__name__, e.message
            )
        )

    return True


def create_session():
    return db.session


def commit_session(session, quiet=False):
    try:
        session.commit()
        return True
    except Exception as e:
        err_msg = "Error commiting DB session with error: {}".format(e.message)
        raise Exception(err_msg)

        return False


def ensure_args(params, session):
    params = params or {}
    session = session or create_session()
    return params, session
