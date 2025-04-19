CREATE TABLE `CrawlInfo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `crawl_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `index_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `access_token` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `access_token_updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `crawl_interval` int NOT NULL,
  `last_crawl_time` timestamp NULL DEFAULT NULL,
  `next_crawl_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `crawl_id` (`crawl_id`),
  UNIQUE KEY `index_name` (`index_name`),
  UNIQUE KEY `access_token` (`access_token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `CrawlHistory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `crawl_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `crawl_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `crawl_status` enum('pending','in_progress','success','failed','skipped') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `crawl_error` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `crawl_duration` int NOT NULL,
  `crawl_data_number` int NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `crawl_id` (`crawl_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;