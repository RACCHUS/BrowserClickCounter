from gui import ClickCounterGUI


if __name__ == '__main__':
    try:
        app = ClickCounterGUI()
        app.run()
    except ImportError as e:
        print('Error: Missing required libraries.')
        print('Please install: pip install -r requirements.txt')
        print(f'Specific error: {e}')
    except Exception as e:
        print(f'Error: {e}')