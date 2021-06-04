/* Add FK*/

/* bh_tournament to gbo_tournament*/
ALTER TABLE `beachhandball_2021`.`bh_tournament`
	DROP FOREIGN KEY `FK_bh_tournament_season.season_tournament`,
	DROP FOREIGN KEY `FK_bh_tournament_season.season_cup_tournament`,
	DROP FOREIGN KEY `FK_bh_tournament_gbo.tournament`;
ALTER TABLE `beachhandball_2021`.`bh_tournament`
	ADD CONSTRAINT `FK_bh_tournament_gbo.tournament` FOREIGN KEY (`gbo_tournament_id`) REFERENCES `gbo`.`tournament` (`id`) ON DELETE NO ACTION,
	ADD CONSTRAINT `FK_bh_tournament_season.season_tournament` FOREIGN KEY (`season_tournament_id`) REFERENCES `season`.`season_tournament` (`id`) ON DELETE CASCADE,
	ADD CONSTRAINT `FK_bh_tournament_season.season_cup_tournament` FOREIGN KEY (`season_cup_tournament_id`) REFERENCES `season`.`season_cup_tournament` (`id`) ON DELETE NO ACTION;

ALTER TABLE `bh_tourn_category`
	DROP FOREIGN KEY `FK_bh_tourn_category_gbo.category`;
ALTER TABLE `beachhandball_2021`.`bh_tourn_category`
	ADD CONSTRAINT `FK_bh_tourn_category_gbo.category` FOREIGN KEY (`gbo_category_id`) REFERENCES `gbo`.`category` (`id`);

/* tevent fk to season category */
ALTER TABLE `bh_tournament_event`
	DROP FOREIGN KEY `FK_bh_tournament_event_season.tournament_category`;
ALTER TABLE `bh_tournament_event`
	ADD CONSTRAINT `FK_bh_tournament_event_season.tournament_category` FOREIGN KEY (`season_tournament_category_id`) REFERENCES `season`.`tournament_category` (`id`) ON DELETE CASCADE;

/* Create INSERT Trigger season_cup_tournament */
CREATE TRIGGER `season_cup_tournament_after_insert` AFTER INSERT ON `season_cup_tournament` FOR EACH ROW BEGIN
INSERT INTO `beachhandball_2021`.`bh_tournament` (`created_at`, `organizer`, `name`, `gbo_data`, `season_cup_tournament_id`, `is_active`, `last_sync_at`, `season_tournament_id`, `gbo_tournament_id`) VALUES (UNIX_TIMESTAMP(), (SELECT subjectId FROM season_subject WHERE id=(SELECT seasonSubjectId FROM season_tournament WHERE id=NEW.seasonTournamentId)), (SELECT `name` FROM gbo.tournament WHERE id=(SELECT tournamentId FROM season_tournament WHERE id=NEW.seasonTournamentId)), '{}', NEW.id, '0', UNIX_TIMESTAMP(), NEW.seasonTournamentId, (SELECT `id` FROM gbo.tournament WHERE id=(SELECT tournamentId FROM season_tournament WHERE id=NEW.seasonTournamentId)));
END;

/* Update tournament*/
CREATE TRIGGER `tournament_after_update` AFTER UPDATE ON `tournament` FOR EACH ROW BEGIN
UPDATE `beachhandball_2021`.`bh_tournament` SET `name`=NEW.name WHERE gbo_tournament_id=NEW.id;
END;


/*gbo category*/
CREATE TRIGGER `category_after_insert` AFTER INSERT ON `category` FOR EACH ROW BEGIN
INSERT INTO `beachhandball_2021`.`bh_tourn_category` (`created_at`, `name`, `abbreviation`, `classification`, `category`, `gbo_category_id`) 
VALUES (UNIX_TIMESTAMP(),(SELECT `name` FROM setup.gender WHERE id=NEW.genderId), '', NEW.name, (SELECT `name` FROM setup.gender WHERE id=NEW.genderId), NEW.id);
END;

/* create tevent per category */
CREATE DEFINER=`tim`@`%` TRIGGER `tournament_category_after_insert` AFTER INSERT ON `tournament_category` FOR EACH ROW BEGIN
INSERT INTO `beachhandball_2021`.`bh_tournament_event` (`created_at`, `name`, `start_ts`, `end_ts`, `max_number_teams`, `is_in_configuration`, `last_sync_at`, `category_id`, `season_cup_tournament_id`, `season_tournament_category_id`, `season_tournament_id`, `tournament_id`, `logo`) 
VALUES (UNIX_TIMESTAMP(),
 (SELECT `name` FROM `beachhandball_2021`.`bh_tournament` WHERE season_tournament_id=NEW.seasonTournamentId),
  UNIX_TIMESTAMP(), UNIX_TIMESTAMP(),
   '16', '0', UNIX_TIMESTAMP(),
	 (SELECT id FROM `beachhandball_2021`.`bh_tourn_category` WHERE gbo_category_id=NEW.categoryId),
	  (SELECT id FROM `season`.`season_cup_tournament` WHERE seasonTournamentId=NEW.seasonTournamentId),
	  NEW.id, NEW.seasonTournamentId,
	  (SELECT id FROM `beachhandball_2021`.`bh_tournament` WHERE season_tournament_id=NEW.seasonTournamentId), 'trophy');
END;