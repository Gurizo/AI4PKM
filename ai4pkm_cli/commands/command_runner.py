class CommandRunner:
    def __init__(self, logger, config=None):
        self.logger = logger
        self.config = config

    def run_command(self, command, arguments, agent):
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
        elif command == "process_notes":
            from .process_notes import ProcessNotes

            notes_processor = ProcessNotes(self.logger, self.config)
            notes_processor.process_notes()
            return True
        elif command == "process_notes_cached" or command == "refine_notes":
            from .process_notes import ProcessNotes

            notes_processor = ProcessNotes(self.logger, self.config)
            notes_processor.process_notes(use_cache=True)
        elif command == "sync-limitless":
            from .sync_limitless_command import SyncLimitlessCommand

            syncer = SyncLimitlessCommand(self.logger)
            syncer.run_sync()
            return True
        elif command == "process_event_data":
            from .process_event_data import ProcessEventData

            processor = ProcessEventData(self.logger, agent)
            event_name = arguments.get("event_name")
            if not event_name:
                self.logger.error("Missing 'event_name' argument for process_event_data")
                return False
            processor.process_files(event_name)
            return True
        elif command == "sync-gobi":
            from .sync_gobi_command import SyncGobiCommand

            syncer = SyncGobiCommand(self.logger)
            syncer.run_sync()
            return True
        elif command == "sync-gobi-by-tags":
            from .sync_gobi_command_by_tags import SyncGobiByTagsCommand

            tags = arguments.get("tags")
            syncer = SyncGobiByTagsCommand(tags, self.logger)
            syncer.run_sync()
            return True
        else:
            self.logger.error(f"Unknown command: {command}")
            return False
