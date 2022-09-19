import sys
from collections import defaultdict

from openvino.runtime import Core, PartialShape
from openvino.pyopenvino import Type

if __name__ == '__main__':
    file_name = sys.argv[1]
    core = Core()
    model = core.read_model(file_name)
    for parameter in model.get_parameters():
        parameter.set_partial_shape(PartialShape.dynamic())
        parameter.set_element_type(Type.dynamic)
    model.validate_nodes_and_infer_types()

    ops_which_stop_dynamic_rank = set()
    ops_which_stop_dynamic_type = set()
    ops_with_dynamic_output_rank = defaultdict(int)
    ops_with_dynamic_element_type = defaultdict(int)

    for op in model.get_ordered_ops():
        op_type_name = "{}::{}".format(op.get_type_info().version_id, op.get_type_name())
        has_dynamically_shaped_inputs = any([input.get_partial_shape().rank.is_dynamic for input in op.inputs()])
        has_dynamically_shaped_outputs = any([output.get_partial_shape().rank.is_dynamic for output in op.outputs()])
        has_dynamically_typed_inputs = any([input.get_element_type().is_dynamic() for input in op.inputs()])
        has_dynamically_typed_outputs = any([output.get_element_type().is_dynamic() for output in op.outputs()])

        if has_dynamically_shaped_inputs and not has_dynamically_shaped_outputs:
            ops_which_stop_dynamic_rank.add(op_type_name)
        elif has_dynamically_shaped_outputs:
            ops_with_dynamic_output_rank[op_type_name] += 1

        if has_dynamically_typed_inputs and not has_dynamically_typed_outputs:
            ops_which_stop_dynamic_type.add(op_type_name)
        elif has_dynamically_typed_outputs:
            ops_with_dynamic_element_type[op_type_name] += 1

    print("ops with dynamic output rank:")
    for name, num_nodes in ops_with_dynamic_output_rank.items():
        print("DYN_OUT_RANK", name, num_nodes)

    print("ops which stop dynamic output rank:")
    for name in ops_which_stop_dynamic_rank:
        print("STOP_DYN_RANK", name)

    print("ops with dynamic output type:")
    for name, num_nodes in ops_with_dynamic_element_type.items():
        print("DYN_OUT_TYPE", name, num_nodes)

    print("ops which stop dynamic element type:")
    for name in ops_which_stop_dynamic_type:
        print("STOP_DYN_TYPE", name)
