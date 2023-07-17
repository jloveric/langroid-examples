import typer

from langroid.agent.chat_agent import ChatAgent, ChatAgentConfig
from langroid.agent.special.recipient_validator_agent import (
    RecipientValidator, RecipientValidatorConfig
)
from langroid.agent.task import Task
from langroid.language_models.openai_gpt import OpenAIChatModel, OpenAIGPTConfig
from langroid.utils.configuration import set_global, Settings
from langroid.utils.logging import setup_colored_logging


app = typer.Typer()

setup_colored_logging()


def chat() -> None:
    config = ChatAgentConfig(
        llm = OpenAIGPTConfig(
            chat_model=OpenAIChatModel.GPT4,
        ),
        vecdb = None,
    )
    student_agent = ChatAgent(config)
    student_task = Task(
        student_agent,
        name = "Student",
        system_message="""
        Your task is to write 4 short bullet points about 
        Language Models in the context of Machine Learning (ML),
        especially about training, and evaluating them. 
        However you are a novice to this field, and know nothing about this topic. 
        To collect your bullet points, you will consult 2 people:
        TrainingExpert and EvaluationExpert.
        You will ask ONE question at a time, to ONE of these experts. 
        To clarify who your question is for, you must use 
        "TO[<recipient>]:" at the start of your message,
        where <recipient> is either TrainingExpert or EvaluationExpert.
        Once you have collected the points you need,
        say DONE, and show me the 4 bullet points. 
        """,
    )
    training_expert_agent = ChatAgent(config)
    training_expert_task = Task(
        training_expert_agent,
        name = "TrainingExpert",
        system_message="""
        You are an expert on Training Language Models in Machine Learning. 
        You will receive questions on this topic, and you must answer these
        very concisely, in one or two sentences, in a way that is easy for a novice to 
        understand.
        """,
        single_round=True,  # task done after 1 step() with valid response
    )

    evaluation_expert_agent = ChatAgent(config)
    evaluation_expert_task = Task(
        evaluation_expert_agent,
        name = "EvaluationExpert",
        system_message="""
        You are an expert on Evaluating Language Models in Machine Learning. 
        You will receive questions on this topic, and you must answer these
        very concisely, in one or two sentences, in a way that is easy for a novice to 
        understand.
        """,
        single_round=True,  # task done after 1 step() with valid response
    )

    validator_agent = RecipientValidator(
        RecipientValidatorConfig(
            recipients=["TrainingExpert", "EvaluationExpert"],
        )
    )
    validator_task = Task(validator_agent, single_round=True)
    student_task.add_sub_task(
        [validator_task, training_expert_task, evaluation_expert_task]
    )
    student_task.run()


@app.command()
def main(
        debug: bool = typer.Option(False, "--debug", "-d", help="debug mode"),
        no_stream: bool = typer.Option(False, "--nostream", "-ns", help="no streaming"),
        nocache: bool = typer.Option(False, "--nocache", "-nc", help="don't use cache"),
) -> None:
    set_global(
        Settings(
            debug=debug,
            cache=not nocache,
            stream=not no_stream,
        )
    )
    chat()


if __name__ == "__main__":
    app()
