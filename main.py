import json

from graph.agent import chatbot
from langchain_core.messages import HumanMessage


def main():

    config = {
    "configurable": {
        "thread_id": "test_user_1"
    }
}

    print("=" * 60)
    print("🔥 ISSUE REPORT AGENT")
    print("=" * 60)

    print("Type 'exit' to quit.")

    while True:

        user_input = input("\nYou → ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break

        if not user_input:
            continue

        initial_state = {
            "messages": [
                HumanMessage(
                    content=user_input
                )
            ]
        }

        try:

            result = chatbot.invoke(
                initial_state,
                config=config
                    )

            final_output = result["messages"][-1]

            print("\nAI →")

            # -----------------------------------------
            # Normal conversation
            # -----------------------------------------

            if result.get("intent") == "normal":

                print(final_output.content)

            # -----------------------------------------
            # Issue report
            # -----------------------------------------

            elif result.get("intent") == "report_issue":

                try:

                    data = json.loads(
                        final_output.content
                    )

                    print(
                        json.dumps(
                            data,
                            indent=2,
                            ensure_ascii=False
                        )
                    )

                except json.JSONDecodeError:

                    # Agent is still talking to the user
                    print(final_output.content)

            else:

                print(final_output.content)

        except Exception as e:

            print("\n❌ ERROR:")
            print(e)


if __name__ == "__main__":
    main()