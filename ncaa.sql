-- MySQL dump 10.13  Distrib 5.1.66, for debian-linux-gnu (i486)
--
-- Host: localhost    Database: ncaa
-- ------------------------------------------------------
-- Server version	5.1.66-0ubuntu0.10.04.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `game`
--

DROP TABLE IF EXISTS `game`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `game` (
  `gameid` int(10) NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `team1` int(5) DEFAULT NULL,
  `team2` int(5) DEFAULT NULL,
  `espnid` int(10) DEFAULT NULL,
  PRIMARY KEY (`gameid`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `play`
--

DROP TABLE IF EXISTS `play`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `play` (
  `gameid` int(10) DEFAULT NULL,
  `segment` tinyint(2) DEFAULT NULL,
  `time` smallint(5) DEFAULT NULL,
  `away_action` text,
  `away_score` tinyint(2) unsigned DEFAULT NULL,
  `home_action` text,
  `home_score` tinyint(2) unsigned DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `player`
--

DROP TABLE IF EXISTS `player`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `player` (
  `playerid` int(10) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `schoolid` int(5) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `player_record`
--

DROP TABLE IF EXISTS `player_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `player_record` (
  `playerid` int(10) NOT NULL DEFAULT '0',
  `gameid` int(10) NOT NULL DEFAULT '0',
  `teamid` int(5) DEFAULT NULL,
  `2pa` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `2pm` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `3pa` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `3pm` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `fta` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `ftm` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `oreb` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `dreb` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `points` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `fouls` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `turnovers` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `steals` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `assists` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `blocks` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `minutes` tinyint(2) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`playerid`,`gameid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `team`
--

DROP TABLE IF EXISTS `team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `team` (
  `teamid` int(5) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`teamid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-01-15 21:28:07
