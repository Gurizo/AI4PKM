class CommandRunner:
    def __init__(self, logger, config=None):
        self.logger = logger
        self.config = config

    def run_command(self, command, agent):
        if command == "process_photos":
            from .process_photos import ProcessPhotos
            photo_processor = ProcessPhotos(self.logger, self.config)
            photo_processor.process_photos()
            return True
        elif command == "generate_report":
            from .generate_report import GenerateReport
            report_generator = GenerateReport(self.logger, agent)
            report_generator.generate_interactive_report()
            return True
        else:
            self.logger.error(f"Unknown command: {command}")
            return False