from pydantic import BaseModel

import fastworkflow
from fastworkflow.session import Session

from ...get_status.parameter_extraction.signatures import (
    CommandParameters as GetStatusCommandParameters,
)
from ...get_status.response_generation.command_implementation import (
    process_command as get_status,
)
from ..parameter_extraction.signatures import CommandParameters


class CommandProcessorOutput(BaseModel):
    target_workitem_found: bool
    status_of_target_workitem: str


def process_command(
    session: Session, input: CommandParameters
) -> CommandProcessorOutput:
    """
    Move to the work-item specified by the given path and optional id.

    :param input: The input parameters for the function.
    """
    workitem = session.workflow_snapshot.workflow.find_workitem(
        input.workitem_path, input.workitem_id
    )

    target_workitem_found = workitem is not None
    if target_workitem_found:
        session.workflow_snapshot.active_workitem = workitem

    active_workitem = session.workflow_snapshot.active_workitem

    get_status_tool_output = get_status(
        session,
        GetStatusCommandParameters(
            workitem_path=active_workitem.path, workitem_id=active_workitem.id
        ),
    )
    return CommandProcessorOutput(
        target_workitem_found=target_workitem_found,
        status_of_target_workitem=get_status_tool_output.status,
    )


if __name__ == "__main__":
    # create a session id
    session_id = 1234
    session = Session(session_id, "shared/tests/lighthouse/workflows/accessreview")

    command_input = CommandParameters(workitem_path="leavers", workitem_id=None)
    output = process_command(session, command_input)
    print(output)
