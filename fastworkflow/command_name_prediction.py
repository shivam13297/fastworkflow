import os
import random

import fastworkflow
from fastworkflow import Action, CommandOutput
from fastworkflow.command_executor import CommandExecutor

def guess_command_name(
    workflow_session: fastworkflow.WorkflowSession,
    command: str,
) -> CommandOutput:
    startup_action = Action(
        workitem_type="command_name_prediction",
        command_name="*",
        command=command,
    )

    # if we are already in the command name prediction workflow, we can just perform the action
    if workflow_session.session.workflow_snapshot.workflow.type == "command_name_prediction":
        command_executor = CommandExecutor()
        command_output = command_executor.perform_action(workflow_session.session, startup_action)
        if len(command_output.command_responses) > 1:
            raise ValueError("Multiple command responses returned from parameter extraction workflow")    
        return (workflow_session.session.id, command_output)    

    fastworkflow_folder = os.path.dirname(os.path.abspath(__file__))
    commandname_prediction_workflow_folderpath = os.path.join(
        fastworkflow_folder, "_workflows", "command_name_prediction"
    )

    context = {
        "subject_workflow_snapshot": workflow_session.session.workflow_snapshot
    }

    command_name_prediction_workflow_session_id = random.randint(1, 100000000)
    workflow_session = fastworkflow.WorkflowSession(
        workflow_session.command_router,
        workflow_session.command_executor,
        command_name_prediction_workflow_session_id, 
        commandname_prediction_workflow_folderpath,
        context=context,
        startup_action=startup_action, 
        keep_alive=False,
        user_message_queue=workflow_session.user_message_queue,
        command_output_queue=workflow_session.command_output_queue,
    )

    command_output = workflow_session.start()
    return (command_name_prediction_workflow_session_id, command_output)

