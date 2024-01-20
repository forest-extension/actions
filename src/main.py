import click
import threading

from command import *


class ConcurrencyCommand(click.Command):
    def invoke(self, ctx):
        thread = threading.Thread(target=self._do_invoke, args=(ctx,))
        thread.start()

    def _do_invoke(self, ctx):
        super().invoke(ctx)


@click.group()
def cli():
    pass


@cli.command(cls=ConcurrencyCommand)
@click.option(
    "-org",
    "--organization",
    default="forest-extension",
    help="Github Organization name",
)
@click.option(
    "-d",
    "--dest",
    help="Destination repository name ex) plugin-test-inven-collector",
    required=True,
)
@click.option(
    "--workflow-type",
    help="plugin",
    default="plugin",
)
def actions(**params):
    run_actions(**params)


@cli.command(cls=ConcurrencyCommand)
@click.option(
    "-org",
    "--organization",
    default="forest-extension",
    help="Github Organization name",
)
@click.option(
    "-d",
    "--dest",
    help="Destination repository name ex) plugin-test-inven-collector",
    required=True,
)
@click.option(
    "-t",
    "--resource-type",
    help="Repository type ex) inventory.Collector, cost-analysis.DataSource, notification.Notification, "
    "monitoring.Webhook, identity.ExternalAuth",
    required=True,
)
@click.option(
    "--workflow-type",
    help="plugin",
    default="plugin",
)
@click.option(
    "--core-version",
    help="Core version ex) 2.0",
    default="2.0",
    required=True,
)
def template(**params):
    run_template(**params)


if __name__ == "__main__":
    cli()
