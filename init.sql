/*
SQLyog Community v9.62 
MySQL - 5.6.26 : Database - sprider
*********************************************************************
*/


/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*Table structure for table `t_product` */

CREATE TABLE `t_product` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '逻辑主键',
  `webdomain` varchar(500) NOT NULL COMMENT '网站域名',
  `prod_id` varchar(200) NOT NULL COMMENT '网站商品id',
  `cat_id` varchar(200) DEFAULT NULL COMMENT '分类id',
  `cat_name` varchar(200) DEFAULT NULL COMMENT '分类名称',
  `prod_name` varchar(2000) DEFAULT NULL COMMENT '商品名',
  `prod_price` varchar(200) DEFAULT NULL COMMENT '价格',
  `prod_price_app` varchar(200) DEFAULT NULL COMMENT 'app价格',
  `prod_imgs` longtext COMMENT '图片地址，为json列表格式',
  `brand_name` varchar(200) DEFAULT NULL COMMENT '品牌',
  `comment_count` varchar(200) DEFAULT NULL COMMENT '评价数',
  `orig_country` varchar(200) DEFAULT NULL COMMENT '原产地',
  `discount` varchar(200) DEFAULT NULL COMMENT '折扣',
  `favorite_count` varchar(200) DEFAULT NULL COMMENT '收藏数',
  `prod_props` longtext COMMENT '商品属性',
  `tax_rate` varchar(200) DEFAULT NULL COMMENT '税率',
  `market_price` varchar(200) DEFAULT NULL COMMENT '市场价',
  `member_count` varchar(200) DEFAULT NULL COMMENT 'X件装',
  `member_price` varchar(200) DEFAULT NULL COMMENT '折合单价',
  `member_price_app` varchar(200) DEFAULT NULL COMMENT 'App折合单价',
  `suggest_price` varchar(200) DEFAULT NULL COMMENT '建议价',
  `warehouse_city` varchar(200) DEFAULT NULL COMMENT '保税区',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `t_taobao_top` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sprider_date` varchar(10) NOT NULL COMMENT '抓取日期',
  `cat1` varchar(200) DEFAULT NULL COMMENT '分类1',
  `cat2` varchar(200) DEFAULT NULL COMMENT '分类2',
  `cat3` varchar(200) DEFAULT NULL,
  `top_name` varchar(200) DEFAULT NULL COMMENT '排行榜名称',
  `focus` int(11) DEFAULT NULL COMMENT '排名',
  `key_word` varchar(200) DEFAULT NULL COMMENT '关键字',
  `url` varchar(1000) DEFAULT NULL,
  `num` decimal(10,0) DEFAULT NULL COMMENT '关注指数',
  `percent` varchar(50) DEFAULT NULL,
  `uod_pos` int(11) DEFAULT NULL COMMENT '升降位次',
  `uod_pos_arrow` int(11) DEFAULT NULL COMMENT '升降位次方向   0下降1上升2平',
  `uod_percent` varchar(50) DEFAULT NULL COMMENT '升降幅度',
  `uod_percent_arrow` int(11) DEFAULT NULL COMMENT '升降幅度方向    0下降1上升2平',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
