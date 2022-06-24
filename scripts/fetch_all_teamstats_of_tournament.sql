SELECT `item`.`id` AS `item_id`, 
	`item`.`name` AS `item_name`, 
        `item`.`abbreviation` AS `item_abbreviation`, 
        `item`.`is_dummy` AS `item_is_dummy`, 
        `item`.`season_team_cup_tournament_ranking_id` AS `item_season_team_cup_tournament_ranking_id`, 
        `bhCategory`.`gbo_category_id` AS `bhCategory_gbo_category_id`, 
        `bhTeamStats`.`id` AS `bhTeamStats_id`, 
        `bhTeamStats`.`tournament_event_id` AS `bhTeamStats_tournament_event_id`, 
        `bhTeamStats`.`tournamentstate_id` AS `bhTeamStats_tournamentstate_id`, 
        `bhTeamStats`.`team_id` AS `bhTeamStats_team_id`, 
        `bhTournamentEvent`.`id` AS `bhTournamentEvent_id`, 
        `bhTournamentEvent`.`tournament_id` AS `bhTournamentEvent_tournament_id`,
	`bhTournamentState`.`id` AS `bhTournamentState_id`, 
        `bhTournamentState`.`name` AS `bhTournamentState_name`, 
        `bhTournamentState`.`abbreviation` AS `bhTournamentState_abbreviation`, 
        `bhTournamentState`.`is_final` AS `bhTournamentState_is_final`, 
        `bhTournamentState`.`hierarchy` AS `bhTournamentState_hierarchy`,
        `bhTournamentState`.`round_type` AS `bhTournamentState_round_type`,
        `bhTournamentStage`.`id` AS `bhTournamentStage_id`, 
        `bhTournamentStage`.`tournament_stage` AS `bhTournamentStage_tournament_stage`, 
        `bhTournamentStage`.`order` AS `bhTournamentStage_order`
FROM `beachhandball_2022`.`bh_team` AS `item` 
	INNER JOIN `beachhandball_2022`.`bh_tourn_category` `bhCategory` ON `bhCategory`.`id`=`item`.`category_id`  
        INNER JOIN `beachhandball_2022`.`bh_team_stats` `bhTeamStats` ON `bhTeamStats`.`team_id`=`item`.`id`  
        INNER JOIN `beachhandball_2022`.`bh_tournament_event` `bhTournamentEvent` ON `bhTournamentEvent`.`id`=`bhTeamStats`.`tournament_event_id`  
        INNER JOIN `beachhandball_2022`.`bh_tournament_states` `bhTournamentState` ON `bhTournamentState`.`id`=`bhTeamStats`.`tournamentstate_id`  
        INNER JOIN `beachhandball_2022`.`bh_tournament_stage` `bhTournamentStage` ON `bhTournamentStage`.`id`=`bhTournamentState`.`tournament_stage_id`  
        INNER JOIN `beachhandball_2022`.`bh_team` `bhTeam` ON `bhTeam`.`id`=`bhTeamStats`.`team_id` 
WHERE (`item`.`season_cup_tournament_id` = 23) AND (item.category_id = 1);
