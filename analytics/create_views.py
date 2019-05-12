import couchdb


def create_view(url, db_name, view_name, mapFunc, reduceFunc=None, overwrite=False):
    server = couchdb.Server(url=url)
    db = server[db_name]
    design_doc = db.get("_design/analyze")
    view_path = "_design/analyze/_view/{}".format(view_name)
    if design_doc is None:
        new_design_doc = {"_id": "_design/analyze", "views": {view_name: {"map": mapFunc}}, "language": "javascript"}
        db.save(new_design_doc)
        return view_path
    else:
        if view_name in design_doc["views"]:
            if overwrite:
                design_doc["views"][view_name] = {"map": mapFunc}
                db.save(design_doc)
                return view_path
            else:
                return view_path
        else:
            design_doc["views"].update({view_name: {"map": mapFunc}})
            db.save(design_doc)
            return view_path
