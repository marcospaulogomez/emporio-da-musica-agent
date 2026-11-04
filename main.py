import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from src.agent import EmporioMusicAgent

console = Console()


def print_banner():
    banner_text = (
        "🎸 **EMPÓRIO DA MÚSICA — Assistente Virtual de Atendimento**\n"
        "_Sua música começa aqui! (Campo Grande / MS)_\n\n"
        "**Comandos disponíveis:**\n"
        "- Digite sua dúvida ou mensagem normalmente\n"
        "- `/historico` para visualizar o histórico salvo da conversa\n"
        "- `/limpar` para reiniciar a conversa\n"
        "- `/sair` para encerrar o atendimento"
    )
    console.print(Panel(Markdown(banner_text), border_style="cyan", title="Bem-vindo(a)"))


def show_history(agent: EmporioMusicAgent):
    if not agent.memory.turns:
        console.print("[yellow]Nenhuma mensagem registrada nesta sessão ainda.[/yellow]")
        return

    console.print("\n[bold cyan]📜 Histórico da Conversa:[/bold cyan]")
    for idx, turn in enumerate(agent.memory.turns, start=1):
        ts = turn.get("timestamp", "")
        console.print(f"[bold green][{idx}] Você ({ts}):[/bold green] {turn['user']}")
        console.print(f"[bold magenta]Assistente:[/bold magenta] {turn['assistant']}\n")


def run_cli():
    print_banner()

    try:
        agent = EmporioMusicAgent()
    except Exception as exc:
        console.print(f"[bold red]Erro ao inicializar o agente:[/bold red] {exc}")
        sys.exit(1)

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]Você[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[cyan]Encerrando atendimento. Até logo e boa música! 🎶[/cyan]")
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in {"/sair", "sair", "exit", "quit"}:
            console.print("\n[cyan]Obrigado por falar com a Empório da Música! Até a próxima! 🎶[/cyan]")
            break
        if cmd in {"/limpar", "limpar", "reset"}:
            agent.reset()
            console.print("[yellow]🔄 Histórico de conversa reiniciado![/yellow]")
            continue
        if cmd in {"/historico", "historico"}:
            show_history(agent)
            continue

        with console.status("[bold cyan]Consultando sistema da Empório da Música...[/bold cyan]", spinner="dots"):
            reply = agent.chat(user_input)

        console.print()
        console.print(
            Panel(
                Markdown(reply),
                title="🎵 Empório da Música",
                border_style="bright_blue",
                padding=(1, 2),
            )
        )


if __name__ == "__main__":
    run_cli()

