"Implementation of the 'init' command."
import logging
import uuid

from cosmic_ray.ast import get_ast, ast_nodes
import cosmic_ray.modules
from cosmic_ray.work_item import WorkItem
from cosmic_ray.plugins import get_operator
from cosmic_ray.work_db import WorkDB

log = logging.getLogger()

def filter_nodes(nodes, lines):
    res = []
    for node in nodes:
        if lines & set(range(node.start_pos[0], node.end_pos[0] + 1)):
            res.append(node)
    return res

def all_work_items(module_paths, operator_names, python_version, filters=None):
    "Iterable of all WorkItems for the given inputs."
    for module_path in module_paths:
        module_ast = get_ast(
            module_path, python_version=python_version)

        nodes = list(ast_nodes(module_ast))
        if filters is not None:
            if module_path not in filters:
                continue
            nodes = filter_nodes(nodes, filters[module_path])

        for op_name in operator_names:
            operator = get_operator(op_name)(python_version)
            occurrence = 0
            for node in nodes:
                for start_pos, end_pos in operator.mutation_positions(node):
                    yield WorkItem(
                        job_id=uuid.uuid4().hex,
                        module_path=str(module_path),
                        operator_name=op_name,
                        occurrence=occurrence,
                        start_pos=start_pos,
                        end_pos=end_pos)

                    occurrence += 1


def init(module_paths, work_db: WorkDB, config, filters=None):
    """Clear and initialize a work-db with work items.

    Any existing data in the work-db will be cleared and replaced with entirely
    new work orders. In particular, this means that any results in the db are
    removed.

    Args:
      module_paths: iterable of pathlib.Paths of modules to mutate.
      work_db: A `WorkDB` instance into which the work orders will be saved.
      config: The configuration for the new session.
      filters: dict of file:lines to keep
    """

    operator_names = list(cosmic_ray.plugins.operator_names())

    work_db.set_config(config=config)

    work_db.clear()
    work_db.add_work_items(
        all_work_items(
            module_paths, 
            operator_names, 
            config.python_version,
            filters=filters))
