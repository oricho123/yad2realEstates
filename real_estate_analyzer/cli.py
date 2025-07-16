"""Command Line Interface for Real Estate Analyzer.

This module provides the CLI commands for the Real Estate Analyzer application.
Using Click framework for better command management and user experience.
"""

from src.data.loaders import PropertyDataLoader
from src.config.settings import get_config
from app import create_app
import sys
import click
from pathlib import Path

# Add package to path for imports
sys.path.insert(0, str(Path(__file__).parent))


@click.group()
@click.version_option(version="2.0.0", prog_name="Real Estate Analyzer")
def cli():
    """🏠 Real Estate Analyzer - Market Analysis Dashboard

    A comprehensive real estate market analysis tool that scrapes property data 
    from Yad2 and provides interactive visualizations, market insights, and 
    investment recommendations.
    """
    pass


@cli.command()
@click.option('--host', '-h', default=None, help='Host to bind to (default: 127.0.0.1)')
@click.option('--port', '-p', type=int, default=None, help='Port to serve on (default: 8051)')
@click.option('--debug/--no-debug', default=None, help='Enable debug mode')
@click.option('--data-dir', type=click.Path(exists=True), help='Custom data directory (legacy option)')
def serve(host, port, debug, data_dir):
    """Start the web dashboard server."""
    click.echo("🏠 Real Estate Analyzer - Starting Dashboard Server")
    click.echo("=" * 55)

    # Get configuration
    config = get_config()

    # Override settings if provided
    actual_host = host or config.SERVER_HOST
    actual_port = port or config.SERVER_PORT
    actual_debug = debug if debug is not None else config.DEBUG

    if actual_debug:
        click.echo("🐛 Debug mode enabled")

    # Load initial data
    try:
        click.echo(
            "🔄 Initializing empty dataset - user data will auto-load from browser storage")
        loader = PropertyDataLoader()
        initial_data = loader.create_empty_dataframe()
    except Exception as e:
        click.echo(f"❌ Failed to initialize data loader: {str(e)}", err=True)
        click.echo("🔄 Starting with empty dataset")
        loader = PropertyDataLoader()
        initial_data = loader.create_empty_dataframe()

    # Create and configure the dashboard application
    click.echo(
        f"\n🚀 Starting dashboard server on http://{actual_host}:{actual_port}")

    try:
        # Create the application
        app = create_app(initial_data)

        click.echo("✅ Dashboard application created successfully")
        click.echo("\n🎯 Dashboard Features Available:")
        click.echo("   • Interactive property filtering and visualization")
        click.echo("   • Dual-view scatter plot and map interface")
        click.echo("   • Advanced analytics dashboard")
        click.echo("   • New data scraping capabilities")
        click.echo("   • Best deals identification")
        click.echo("   • Market insights and recommendations")

        click.echo(
            f"\n🎉 Open your browser to: http://{actual_host}:{actual_port}")
        click.echo("⏹️  Press Ctrl+C to stop the server")

        # Start the server
        app.run(
            debug=actual_debug,
            host=actual_host,
            port=actual_port
        )

    except KeyboardInterrupt:
        click.echo("\n👋 Dashboard stopped by user")
    except Exception as e:
        click.echo(f"\n❌ Error starting dashboard: {str(e)}", err=True)
        click.echo("💡 Try running with --debug for more information")
        sys.exit(1)


@cli.command()
def init():
    """Initialize environment configuration."""
    from setup_env import setup_environment_file

    click.echo("🔧 Initializing Real Estate Analyzer environment...")
    success = setup_environment_file()

    if success:
        click.echo("✅ Environment setup completed!")
        click.echo("\n🎯 Next steps:")
        click.echo("1. Review and edit the .env file as needed")
        click.echo("2. Run: real-estate-analyzer serve")
    else:
        click.echo("❌ Environment setup failed")
        sys.exit(1)


@cli.command()
@click.option('--check-deps/--no-check-deps', default=True, help='Check for missing dependencies')
def doctor(check_deps):
    """Check system health and configuration."""
    click.echo("🩺 Real Estate Analyzer - System Health Check")
    click.echo("=" * 45)

    issues = []

    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
        click.echo("❌ Python version: Too old (requires 3.8+)")
    else:
        click.echo(f"✅ Python version: {sys.version.split()[0]}")

    # Check dependencies
    if check_deps:
        missing_deps = []
        required_packages = ['dash', 'pandas',
                             'plotly', 'requests', 'numpy', 'scipy']

        for package in required_packages:
            try:
                __import__(package)
                click.echo(f"✅ Package: {package}")
            except ImportError:
                missing_deps.append(package)
                click.echo(f"❌ Package: {package} (missing)")

        if missing_deps:
            issues.append(f"Missing packages: {', '.join(missing_deps)}")

    # Check data directory
    config = get_config()
    data_dir = config.DATA_DIRECTORY
    if data_dir.exists():
        click.echo(f"✅ Data directory: {data_dir}")
    else:
        click.echo(f"⚠️  Data directory: {data_dir} (will be created)")

    # Check configuration
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        click.echo(f"✅ Environment file: {env_file}")
    else:
        click.echo(f"⚠️  Environment file: {env_file} (using defaults)")

    # Summary
    if issues:
        click.echo(f"\n❌ Found {len(issues)} issue(s):")
        for issue in issues:
            click.echo(f"   • {issue}")
        click.echo(
            "\n💡 Run 'pip install -r requirements.txt' to fix missing packages")
        sys.exit(1)
    else:
        click.echo("\n🎉 All checks passed! System is healthy.")


@cli.command()
def version():
    """Show version information."""
    click.echo("Real Estate Analyzer v2.0.0")
    click.echo("Python-based real estate market analysis dashboard")
    click.echo("https://github.com/yourusername/real-estate-analyzer")


if __name__ == '__main__':
    cli()
