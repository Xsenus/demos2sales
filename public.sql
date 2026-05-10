/*
 Navicat Premium Dump SQL

 Source Server         : ai.irbistech
 Source Server Type    : PostgreSQL
 Source Server Version : 160013 (160013)
 Source Host           : 79.174.94.14:5464
 Source Catalog        : demo_calc
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 160013 (160013)
 File Encoding         : 65001

 Date: 05/05/2026 15:06:46
*/


-- ----------------------------
-- Sequence structure for demo_expenses_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."demo_expenses_id_seq";
CREATE SEQUENCE "public"."demo_expenses_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for sale_rows_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."sale_rows_id_seq";
CREATE SEQUENCE "public"."sale_rows_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Table structure for actions
-- ----------------------------
DROP TABLE IF EXISTS "public"."actions";
CREATE TABLE "public"."actions" (
  "action_id" text COLLATE "pg_catalog"."default" NOT NULL,
  "action_type" text COLLATE "pg_catalog"."default" NOT NULL,
  "manager_login" text COLLATE "pg_catalog"."default" NOT NULL,
  "sequence_no" int4 NOT NULL,
  "action_date" date NOT NULL,
  "client" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "city" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "model" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "task_description" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "comment" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "is_director_confirmed" bool NOT NULL DEFAULT false,
  "confirmed_amount" numeric(14,2),
  "director_comment" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "created_at" timestamp(6) NOT NULL DEFAULT now(),
  "updated_at" timestamp(6) NOT NULL DEFAULT now(),
  "payload" jsonb NOT NULL DEFAULT '{}'::jsonb
)
;

-- ----------------------------
-- Records of actions
-- ----------------------------
INSERT INTO "public"."actions" VALUES ('MARIA-10', 'Проведенная демонстрация', 'maria', 10, '2026-04-03', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 50000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('MARIA-20', 'Проданное оборудование', 'maria', 20, '2026-04-06', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 51000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('MARIA-30', 'Проведенная демонстрация', 'maria', 30, '2026-04-09', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 52000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('MARIA-40', 'Проданное оборудование', 'maria', 40, '2026-04-12', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 53000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('MARIA-50', 'Проданное оборудование', 'maria', 50, '2026-04-15', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 54000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('MARIA-60', 'Выплата премии', 'maria', 60, '2026-04-18', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 120000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('MARIA-80', 'Проданное оборудование', 'maria', 70, '2026-04-24', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', 17176.00, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('MARIA-90', 'Проведенная демонстрация', 'maria', 80, '2026-04-27', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', 70207.25, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": "8"}}');
INSERT INTO "public"."actions" VALUES ('MARIA-70', 'Проведенная демонстрация', 'maria', 90, '2026-04-21', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('MARIA-100', 'Проданное оборудование', 'maria', 100, '2026-04-30', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('MARIA-110', 'Проведенная демонстрация', 'maria', 110, '2026-05-03', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('MARIA-120', 'Проданное оборудование', 'maria', 120, '2026-05-06', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('MARIA-130', 'Проведенная демонстрация', 'maria', 130, '2026-05-09', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('MARIA-140', 'Проданное оборудование', 'maria', 140, '2026-05-12', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('MARIA-150', 'Выплата премии', 'maria', 150, '2026-05-15', 'Кондитерская фабрика', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-10', 'Проведенная демонстрация', 'ruslan', 10, '2026-04-01', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 50000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-20', 'Проданное оборудование', 'ruslan', 20, '2026-04-04', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 51000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-30', 'Проведенная демонстрация', 'ruslan', 30, '2026-04-07', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 52000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-40', 'Проданное оборудование', 'ruslan', 40, '2026-04-10', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 53000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-50', 'Проданное оборудование', 'ruslan', 50, '2026-04-13', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 54000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-60', 'Выплата премии', 'ruslan', 60, '2026-04-16', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 120000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-70', 'Проведенная демонстрация', 'ruslan', 70, '2026-04-19', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-80', 'Проданное оборудование', 'ruslan', 80, '2026-04-22', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-90', 'Проведенная демонстрация', 'ruslan', 90, '2026-04-25', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-100', 'Проданное оборудование', 'ruslan', 100, '2026-04-28', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-110', 'Проведенная демонстрация', 'ruslan', 110, '2026-05-01', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-120', 'Проданное оборудование', 'ruslan', 120, '2026-05-04', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-130', 'Проведенная демонстрация', 'ruslan', 130, '2026-05-07', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-140', 'Проданное оборудование', 'ruslan', 140, '2026-05-10', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('RUSLAN-150', 'Выплата премии', 'ruslan', 150, '2026-05-13', 'Центр Транс Техмаш', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('TIMUR-10', 'Проведенная демонстрация', 'timur', 10, '2026-04-02', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 50000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('TIMUR-20', 'Проданное оборудование', 'timur', 20, '2026-04-05', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 51000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('TIMUR-30', 'Проведенная демонстрация', 'timur', 30, '2026-04-08', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 52000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('TIMUR-40', 'Проданное оборудование', 'timur', 40, '2026-04-11', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 53000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('TIMUR-50', 'Проданное оборудование', 'timur', 50, '2026-04-14', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 54000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('TIMUR-60', 'Выплата премии', 'timur', 60, '2026-04-17', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 't', 120000.00, 'Подтверждено директором', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('TIMUR-70', 'Проведенная демонстрация', 'timur', 70, '2026-04-20', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('TIMUR-80', 'Проданное оборудование', 'timur', 80, '2026-04-23', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('TIMUR-90', 'Проведенная демонстрация', 'timur', 90, '2026-04-26', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('TIMUR-100', 'Проданное оборудование', 'timur', 100, '2026-04-29', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('TIMUR-110', 'Проведенная демонстрация', 'timur', 110, '2026-05-02', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('TIMUR-120', 'Проданное оборудование', 'timur', 120, '2026-05-05', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('TIMUR-130', 'Проведенная демонстрация', 'timur', 130, '2026-05-08', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{"demo_meta": {"demo_hours": null}}');
INSERT INTO "public"."actions" VALUES ('TIMUR-140', 'Проданное оборудование', 'timur', 140, '2026-05-11', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');
INSERT INTO "public"."actions" VALUES ('TIMUR-150', 'Выплата премии', 'timur', 150, '2026-05-14', 'Полипластик', 'Казань', 'TRANSFORMER 2.0 MAX', 'Демо-задача очистки оборудования', 'Демо-данные', 'f', NULL, '', '2026-05-05 09:50:32.766215', '2026-05-05 09:50:32.766215', '{}');

-- ----------------------------
-- Table structure for app_settings
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_settings";
CREATE TABLE "public"."app_settings" (
  "id" int4 NOT NULL DEFAULT 1,
  "settings" jsonb NOT NULL,
  "updated_at" timestamp(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of app_settings
-- ----------------------------
INSERT INTO "public"."app_settings" VALUES (1, '{"k1": 0.65,"ui": {"field_gap_px": 8,"font_base_px": 13,"font_title_px": 18,"card_padding_px": 10,"table_row_height_px": 30,"action_list_width_pct": 30,"criteria_name_width_pct": 20,"criteria_levels_width_pct": 60,"criteria_comment_width_pct": 20,"geo_api_key": ""},"criteria": [{"block": "P","code": "P1","title": "Покупающий центр подтвержден","desc": "оценивает, кто со стороны клиента реально участвует в демонстрации и согласовании. Максимальный балл ставится только если есть и технический инициатор, и руководитель / ЛПР.","levels": [["Участники не подтверждены",0],["Только пользователь / мастер",5],["Есть руководитель 2 или 3 уровня",10],["Есть руководитель организации",15]]},{"block": "P","code": "P2","title": "Объект очистки определен","desc": "оценивает, есть ли конкретный объект, который будут чистить. Максимальный балл — если объект заранее выбран, сфотографирован и признан клиентом приоритетным.","levels": [["Объект не выбран",0],["Объект назван устно",5],["Объект назван и есть фото / видео",10],["Заполнена анкета (лили имеется аналог данных из анкеты) и есть фото",15]]},{"block": "P","code": "P3","title": "Загрязнение и текущий метод очистки описаны","desc": "оценивает, понятно ли, что именно нужно удалить и чем клиент чистит сейчас. Это важно, чтобы не ехать “просто показать аппарат”.","levels": [["Загрязнение не описано",0],["Описано только загрязнение",4],["Описаны загрязнение и текущий метод",7],["Заполнена анкета (лили имеется аналог данных из анкеты) и есть фото",10]]},{"block": "P","code": "P4","title": "Воздух и площадка подтверждены","desc": "оценивает готовность пневмосети и места проведения. Максимальный балл — если подтверждены давление, расход, подключение, доступ, безопасность и условия площадки.","levels": [["Данные по воздуху отсутствуют",0],["Подтверждено только давление",5],["Подтверждены давление и расход",10],["Заполнена анкета (лили имеется аналог данных из анкеты) и есть фото",15]]},{"block": "P","code": "P5","title": "Критерии успеха согласованы","desc": "оценивает, договорились ли заранее, что считается успешной демонстрацией. Это снижает споры после показа.","levels": [["Критерии не согласованы",0],["Есть устное ожидание результата",5],["Согласованы качество и время очистки",10],["Заполнена анкета (лили имеется аналог данных из анкеты) и есть фото",15]]},{"block": "P","code": "P6","title": "Коммерческий потенциал понятен","desc": "оценивает, есть ли связь между демонстрацией и будущей продажей. Максимальный балл — когда понятны модель, бюджет, срок и следующий коммерческий шаг.","levels": [["Коммерческий потенциал не понятен",0],["Есть общий интерес",5],["Понятна возможная модель или бюджет",10],["Понятны модель, бюджет, срок и следующий шаг",15]]},{"block": "P","code": "P7","title": "Логистика и бюджет выезда согласованы","desc": "оценивает, подготовлены ли маршрут, лед, транспорт, люди и бюджет. Максимальный балл — если выезд согласован до начала расходов.","levels": [["Логистика не согласована",0],["Согласованы маршрут и участники",5],["Согласованы маршрут, участники, лед, транспорт и бюджет",10]]},{"block": "P","code": "P8","title": "Карточка и акнета подготовки заполнена и направлена директору и координатору","desc": "формальный критерий дисциплины. Без заполненной карточки нельзя доказать качество подготовки.","levels": [["Карточка отсутствует",0],["Карточка заполнена частично",3],["Карточка заполнена полностью",5]]},{"block": "R","code": "R1","title": "Согласованный технический результат по очистке обознгаченных загрязнений в акнете/письме достигнут","desc": "оценивает, достигнута ли цель очистки, согласованная до демонстрации.","levels": [["Результат не достигнут",0],["Результат достигнут частично",8],["Результат достигнут полностью",15],["Результат достигнут лучше согласованных критериев",20]]},{"block": "R","code": "R2","title": "Измерения зафиксированы","desc": "оценивает, есть ли цифры, а не только впечатление. Максимальный балл — если зафиксированы время, расход льда, давление, сопло и площадь / деталь.","levels": [["Измерений нет",0],["Есть только фото / видео",5],["Есть время или расход льда",10],["Есть время, расход льда, давление, сопло и площадь / деталь",15]]},{"block": "R","code": "R3","title": "Клиент подтвердил результат","desc": "оценивает, кто со стороны клиента увидел и подтвердил результат. Максимальный балл — если результат подтвердил руководитель / ЛПР или технический руководитель.","levels": [["Подтверждения клиента нет",0],["Подтвердил пользователь / мастер",5],["Есть руководитель 2 или 3 уровня",10],["Есть руководитель организации",15]]},{"block": "R","code": "R4","title": "Следующий шаг после демонстрации получен","desc": "главный коммерческий критерий результата. Максимальный балл — если клиент запросил КП, счет, аренду, договор или повторный тест по конкретной сделке.","levels": [["Следующего шага нет",0],["Есть только устный интерес",5],["Назначена дата следующего контакта / встречи",12],["Запрошены КП, счет, аренда, договор или повторный тест",20]]},{"block": "R","code": "R5","title": "Отчет по демонстрации оформлен","desc": "отчет нужен для внутреннего согласования у клиента и для контроля внутри ИРБИСТЕХ.","levels": [["Отчета нет",0],["Есть краткий отчет с фото / видео",5],["Есть отчет с фото / видео, цифрами и выводом",10]]},{"block": "R","code": "R6","title": "Экономика для клиента посчитана","desc": "оценивает, удалось ли перевести технический результат в деньги: простой, труд, расходники, брак, ресурс оборудования.","levels": [["Экономика не обсуждалась",0],["Есть оценка эффекта словами",5],["Есть расчет в часах, рублях или человеко-часах",10]]},{"block": "R","code": "R7","title": "Причина неуспеха или отказа зафиксирована","desc": "этот критерий нужен, если демонстрация не привела сразу к продаже. Важно понять: проблема в технологии, клиенте, бюджете, воздухе, подготовке или сроках.","levels": [["Причина не зафиксирована",0],["Причина описана устно",5],["Причина зафиксирована письменно и есть дальнейшее решение",10]]},{"block": "M","code": "M1","title": "Стратегический статус клиента подтвержден","desc": "снижает вычет, если клиент важен для компании: крупный холдинг, отраслевой лидер, возможны повторные продажи или публичный кейс.","levels": [["Стратегический статус не запрашивался у директора",0],["Статус не директором до выезда",8],["Статус подтвержден директором до выезда",15]]},{"block": "M","code": "M4","title": "Логистика выезда оптимизирована","desc": "снижает вычет, если расходы распределяются не на одну демонстрацию, а на несколько задач маршрута.","levels": [["1 клиент Х демо",0],["2 клиент Х демо",5],["3 клиент Х демо и более",10]]},{"block": "M","code": "M6","title": "Демонстрация дала маркетинговую или R&D-ценность","desc": "снижает вычет, если демонстрация полезна не только для одной сделки, но и для будущих продаж: фото, видео, новый кейс, новая отрасль, проверка новой задачи.","levels": [["Материалы непригодны для повторного использования",0],["Материалы пригодны только внутри компании",7],["Материалы пригодны для кейса / маркетинга (фото 16:9 и видео 16:9)",15]]}],"m_weight": 0.2,"p_weight": 0.45,"r_weight": 0.35,"vat_rate": 0.22,"font_family": "Arial","min_normal_k": 0.2,"office_rates": {"Казань": {"driver_km_rate": 15.0,"demo_work_rate": 1350.0,"cryoblaster_rate": 4000.0,"gazelle_rate": 18000.0,"sale_st": 0.565,"latitude": 55.796127,"longitude": 49.106414},"Москва": {"driver_km_rate": 18.0,"demo_work_rate": 1350.0,"cryoblaster_rate": 4500.0,"gazelle_rate": 22000.0,"sale_st": 0.465,"latitude": 55.7987966,"longitude": 37.965255}},"office_cities": ["Казань","Москва"],"min_soft_stop_k": 0.8,"expense_settings": [{"code": "d_driver_km","article": "Работа водителя за километраж по маячку А5/А6","section": "driver","unit": "км","qty_default": 300,"price_net_default": 0,"price_vat_default": 0,"qty_manager": true,"price_manager": false,"calc_type": "office_driver_km","comment": "Количество вводит менеджер; ставка NET на руки подставляется по офису менеджера; НПД считается через 0.94"},{"code": "d_demo_work","article": "Работа демонстратора*","section": "driver","unit": "часы","qty_default": 4,"price_net_default": 1350,"price_vat_default": 0,"qty_manager": false,"price_manager": false,"calc_type": "demo_work_total","comment": "Количество = время на административные процедуры + время работы на демонстрации; ставка NET на руки подставляется по офису менеджера; НПД считается через 0.94"},{"code": "d_night_compensation","article": "Компенсация за ночевку и другие согласованные расходы","section": "driver","unit": "руб. на руки","qty_default": 0,"price_net_default": 0,"price_vat_default": 0,"qty_manager": true,"price_manager": false,"calc_type": "npd_cash_input","comment": "Менеджер вводит сумму на руки; НПД считается через 0.94"},{"code": "d_cryoblaster","article": "Демонстрация криобластера (1 демо = 1 точка Газели)","section": "driver","unit": "усл","qty_default": 1,"price_net_default": 0,"price_vat_default": 0,"qty_manager": true,"price_manager": false,"calc_type": "office_cryoblaster","comment": "Количество вводит менеджер; ставка NET на руки подставляется по офису менеджера; НПД считается через 0.94"},{"code": "d_hard_conditions","article": "Усложненные условия труда","section": "driver","unit": "усл","qty_default": 0,"price_net_default": 1700,"price_vat_default": 0,"qty_manager": true,"price_manager": false,"calc_type": "npd_direct","comment": "Жара/холод/дождь/снег/противогаз/грязная или шумная среда/улица/сложный допуск, если указано в акте"},{"code": "d_electric_compressor","article": "Работа с электрическим компрессором в фанере","section": "driver","unit": "усл","qty_default": 0,"price_net_default": 3500,"price_vat_default": 0,"qty_manager": true,"price_manager": false,"calc_type": "npd_direct","comment": "Административная ставка; количество вводит менеджер"},{"code": "d_electro_reel","article": "Использование электрокатушки","section": "driver","unit": "усл","qty_default": 1,"price_net_default": 1000,"price_vat_default": 0,"qty_manager": true,"price_manager": true,"calc_type": "npd_direct","comment": "Менеджер может менять количество и ставку NET на руки"},{"code": "d_load_unload","article": "Выгрузка и загрузка компрессора и электрокатушки","section": "driver","unit": "усл","qty_default": 0,"price_net_default": 2000,"price_vat_default": 0,"qty_manager": true,"price_manager": true,"calc_type": "npd_direct","comment": "Снятие/монтаж ремней, подготовка к перемещению, перемещение на колесах/платформе или с механизацией"},{"code": "o_transport_fixed","article": "Расходы на перевозку чужим транспортом (туда-обратно)","section": "other","unit": "усл","qty_default": 0,"price_net_default": 2800,"price_vat_default": 0,"qty_manager": true,"price_manager": true,"calc_type": "direct","comment": "Менеджерское поле"},{"code": "o_transport_km","article": "Расходы на перевозку чужим транспортом (туда-обратно)","section": "other","unit": "км","qty_default": 0,"price_net_default": 41,"price_vat_default": 0,"qty_manager": true,"price_manager": true,"calc_type": "direct","comment": "Менеджерское поле по километражу стороннего транспорта"},{"code": "o_hotel_manager","article": "Расходы на отель Менеджера","section": "other","unit": "день х чел","qty_default": 0,"price_net_default": 2800,"price_vat_default": 0,"qty_manager": true,"price_manager": true,"calc_type": "direct","comment": "Менеджерское поле"},{"code": "o_hotel_driver","article": "Расходы на отель Водителя","section": "other","unit": "день х чел","qty_default": 0,"price_net_default": 2800,"price_vat_default": 0,"qty_manager": true,"price_manager": true,"calc_type": "direct","comment": "Менеджерское поле"},{"code": "o_manager_travel","article": "Расходы на переезд менеджера","section": "other","unit": "усл","qty_default": 0,"price_net_default": 3000,"price_vat_default": 0,"qty_manager": true,"price_manager": true,"calc_type": "direct","comment": "Менеджерское поле"},{"code": "o_toll","article": "Расходы на платную дорогу (туда-обратно) по транспондеру","section": "other","unit": "усл","qty_default": 0,"price_net_default": 0,"price_vat_default": 0,"qty_manager": true,"price_manager": false,"calc_type": "cash_amount_vat","comment": "Менеджер вводит сумму платежа; сумма попадает в расходы с НДС как в Excel"},{"code": "o_per_diem","article": "Суточные по командировки (при ночевке)","section": "other","unit": "день х чел","qty_default": 1,"price_net_default": 1500,"price_vat_default": 0,"qty_manager": true,"price_manager": false,"calc_type": "direct","comment": "Количество вводит менеджер; ставка административная"},{"code": "o_diesel","article": "Расходы на дизель (15 л/100км), л","section": "other","unit": "литры","qty_default": 0,"price_net_default": 0,"price_vat_default": 72,"qty_manager": false,"price_manager": true,"calc_type": "diesel","comment": "Количество = километраж / 100 × 15; цена с НДС вводится менеджером"},{"code": "o_gazelle_amort","article": "Амортизация Газели и ТО","section": "other","unit": "усл","qty_default": 1,"price_net_default": 0,"price_vat_default": 0,"qty_manager": true,"price_manager": false,"calc_type": "office_gazelle_amort_total","comment": "Количество корректирует менеджер; административная ставка подставляется по офису менеджера"},{"code": "o_dry_ice_purchase","article": "Расходы на закупку сухого льда","section": "other","unit": "кг","qty_default": 30,"price_net_default": 0,"price_vat_default": 110,"qty_manager": true,"price_manager": true,"calc_type": "direct_vat_price","comment": "Менеджерское поле: количество и цена с НДС"},{"code": "o_dry_ice_delivery","article": "Расходы на доставку сухого льда в цех","section": "other","unit": "усл","qty_default": 0,"price_net_default": 1500,"price_vat_default": 0,"qty_manager": true,"price_manager": true,"calc_type": "direct","comment": "Менеджерское поле"}],"payroll_tax_rate": 0.3,"diesel_l_per_100km": 15.0,"k_reduction_factor": 0.8,"npd_factor": 0.94,"driver_avg_speed_kmh": 75.0}', '2026-05-05 09:50:32.766215');

-- ----------------------------
-- Table structure for app_users
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_users";
CREATE TABLE "public"."app_users" (
  "login" text COLLATE "pg_catalog"."default" NOT NULL,
  "password" text COLLATE "pg_catalog"."default" NOT NULL,
  "role" text COLLATE "pg_catalog"."default" NOT NULL,
  "name" text COLLATE "pg_catalog"."default" NOT NULL,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamp(6) NOT NULL DEFAULT now(),
  "office_city" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'Казань'::text
)
;

-- ----------------------------
-- Records of app_users
-- ----------------------------
INSERT INTO "public"."app_users" VALUES ('artur', '123', 'director', 'Артур Гимадеев', 't', '2026-05-05 09:50:32.766215', 'Казань');
INSERT INTO "public"."app_users" VALUES ('ildar', '444', 'manager', 'Ильдар Хасанов', 't', '2026-05-05 09:50:32.766215', 'Казань');
INSERT INTO "public"."app_users" VALUES ('maria', '333', 'manager', 'Мария Иванова', 't', '2026-05-05 09:50:32.766215', 'Казань');
INSERT INTO "public"."app_users" VALUES ('ruslan', '111', 'manager', 'Руслан Абдулин', 't', '2026-05-05 09:50:32.766215', 'Казань');
INSERT INTO "public"."app_users" VALUES ('timur', '222', 'manager', 'Тимур Сафин', 't', '2026-05-05 09:50:32.766215', 'Казань');

-- ----------------------------
-- Table structure for demo_criterion_values
-- ----------------------------
DROP TABLE IF EXISTS "public"."demo_criterion_values";
CREATE TABLE "public"."demo_criterion_values" (
  "action_id" text COLLATE "pg_catalog"."default" NOT NULL,
  "criterion_code" text COLLATE "pg_catalog"."default" NOT NULL,
  "level_index" int4 NOT NULL DEFAULT 0,
  "manager_comment" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text
)
;

-- ----------------------------
-- Records of demo_criterion_values
-- ----------------------------
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'P1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'P2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'P3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'P4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'P5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'P6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'P7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'P8', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'R1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'R2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'R3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'R4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'R5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'R6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'R7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'M1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'M2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'M3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'M4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'M5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'M6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-10', 'M7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'P1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'P2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'P3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'P4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'P5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'P6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'P7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'P8', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'R1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'R2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'R3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'R4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'R5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'R6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'R7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'M1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'M2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'M3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'M4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'M5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'M6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-30', 'M7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'P1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'P2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'P3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'P4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'P5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'P6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'P7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'P8', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'R1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'R2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'R3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'R4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'R5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'R6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'R7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'M1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'M2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'M3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'M4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'M5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'M6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-90', 'M7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'P1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'P2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'P3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'P4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'P5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'P6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'P7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'P8', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'R1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'R2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'R3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'R4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'R5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'R6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'R7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'M1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'M2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'M3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'M4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'M5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'M6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-70', 'M7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'P1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'P2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'P3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'P4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'P5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'P6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'P7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'P8', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'R1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'R2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'R3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'R4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'R5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'R6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'R7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'M1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'M2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'M3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'M4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'M5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'M6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-110', 'M7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'P1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'P2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'P3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'P4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'P5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'P6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'P7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'P8', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'R1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'R2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'R3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'R4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'R5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'R6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'R7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'M1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'M2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'M3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'M4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'M5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'M6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('MARIA-130', 'M7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'P1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'P2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'P3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'P4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'P5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'P6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'P7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'P8', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'R1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'R2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'R3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'R4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'R5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'R6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'R7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'M1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'M2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'M3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'M4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'M5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'M6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-10', 'M7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'P1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'P2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'P3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'P4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'P5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'P6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'P7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'P8', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'R1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'R2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'R3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'R4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'R5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'R6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'R7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'M1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'M2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'M3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'M4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'M5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'M6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-30', 'M7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'P1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'P2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'P3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'P4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'P5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'P6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'P7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'P8', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'R1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'R2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'R3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'R4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'R5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'R6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'R7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'M1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'M2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'M3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'M4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'M5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'M6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-70', 'M7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'P1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'P2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'P3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'P4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'P5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'P6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'P7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'P8', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'R1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'R2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'R3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'R4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'R5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'R6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'R7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'M1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'M2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'M3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'M4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'M5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'M6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-90', 'M7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'P1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'P2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'P3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'P4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'P5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'P6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'P7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'P8', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'R1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'R2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'R3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'R4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'R5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'R6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'R7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'M1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'M2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'M3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'M4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'M5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'M6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-110', 'M7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'P1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'P2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'P3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'P4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'P5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'P6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'P7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'P8', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'R1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'R2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'R3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'R4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'R5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'R6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'R7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'M1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'M2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'M3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'M4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'M5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'M6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('RUSLAN-130', 'M7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'P1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'P2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'P3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'P4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'P5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'P6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'P7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'P8', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'R1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'R2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'R3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'R4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'R5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'R6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'R7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'M1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'M2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'M3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'M4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'M5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'M6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-10', 'M7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'P1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'P2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'P3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'P4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'P5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'P6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'P7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'P8', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'R1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'R2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'R3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'R4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'R5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'R6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'R7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'M1', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'M2', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'M3', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'M4', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'M5', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'M6', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-30', 'M7', 2, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'P1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'P2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'P3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'P4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'P5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'P6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'P7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'P8', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'R1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'R2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'R3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'R4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'R5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'R6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'R7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'M1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'M2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'M3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'M4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'M5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'M6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-70', 'M7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'P1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'P2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'P3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'P4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'P5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'P6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'P7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'P8', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'R1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'R2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'R3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'R4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'R5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'R6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'R7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'M1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'M2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'M3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'M4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'M5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'M6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-90', 'M7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'P1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'P2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'P3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'P4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'P5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'P6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'P7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'P8', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'R1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'R2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'R3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'R4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'R5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'R6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'R7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'M1', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'M2', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'M3', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'M4', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'M5', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'M6', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-110', 'M7', 1, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'P1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'P2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'P3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'P4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'P5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'P6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'P7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'P8', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'R1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'R2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'R3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'R4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'R5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'R6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'R7', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'M1', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'M2', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'M3', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'M4', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'M5', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'M6', 0, 'Демо-подтверждение уровня');
INSERT INTO "public"."demo_criterion_values" VALUES ('TIMUR-130', 'M7', 0, 'Демо-подтверждение уровня');

-- ----------------------------
-- Table structure for demo_expenses
-- ----------------------------
DROP TABLE IF EXISTS "public"."demo_expenses";
CREATE TABLE "public"."demo_expenses" (
  "id" int8 NOT NULL DEFAULT nextval('demo_expenses_id_seq'::regclass),
  "action_id" text COLLATE "pg_catalog"."default" NOT NULL,
  "row_order" int4 NOT NULL,
  "row_code" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "article" text COLLATE "pg_catalog"."default" NOT NULL,
  "qty" numeric(14,4) NOT NULL DEFAULT 0,
  "unit" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "price_net" numeric(14,2) NOT NULL DEFAULT 0,
  "price_vat" numeric(14,2) NOT NULL DEFAULT 0,
  "amount_vat" numeric(14,2) NOT NULL DEFAULT 0,
  "calc_type" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'direct'::text,
  "is_custom" bool NOT NULL DEFAULT false,
  "comment" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text
)
;

-- ----------------------------
-- Records of demo_expenses
-- ----------------------------
INSERT INTO "public"."demo_expenses" VALUES (1, 'MARIA-10', 1, 'd_driver_km', 'Работа водителя', 300.0000, 'км', 15.00, 18.30, 5490.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (2, 'MARIA-10', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (3, 'MARIA-10', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (4, 'MARIA-10', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (5, 'MARIA-10', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (6, 'MARIA-10', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (7, 'MARIA-10', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (8, 'MARIA-10', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (9, 'MARIA-10', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (10, 'MARIA-10', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (11, 'MARIA-10', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (12, 'MARIA-10', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (13, 'MARIA-10', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (14, 'MARIA-10', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (15, 'MARIA-10', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (16, 'MARIA-10', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (17, 'MARIA-10', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (18, 'MARIA-30', 1, 'd_driver_km', 'Работа водителя', 300.0000, 'км', 15.00, 18.30, 5490.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (19, 'MARIA-30', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (20, 'MARIA-30', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (21, 'MARIA-30', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (22, 'MARIA-30', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (23, 'MARIA-30', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (24, 'MARIA-30', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (25, 'MARIA-30', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (26, 'MARIA-30', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (27, 'MARIA-30', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (28, 'MARIA-30', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (29, 'MARIA-30', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (30, 'MARIA-30', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (31, 'MARIA-30', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (32, 'MARIA-30', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (33, 'MARIA-30', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (34, 'MARIA-30', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (35, 'MARIA-90', 1, 'd_driver_km', 'Работа водителя', 300.0000, 'км', 15.00, 18.30, 5490.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (36, 'MARIA-90', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (37, 'MARIA-90', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (38, 'MARIA-90', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (39, 'MARIA-90', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (40, 'MARIA-90', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (41, 'MARIA-90', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (42, 'MARIA-90', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (43, 'MARIA-90', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (44, 'MARIA-90', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (45, 'MARIA-90', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (46, 'MARIA-90', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (47, 'MARIA-90', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (48, 'MARIA-90', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (49, 'MARIA-90', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (50, 'MARIA-90', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (51, 'MARIA-90', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (52, 'MARIA-70', 1, 'd_driver_km', 'Работа водителя', 300.0000, 'км', 15.00, 18.30, 5490.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (53, 'MARIA-70', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (54, 'MARIA-70', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (55, 'MARIA-70', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (56, 'MARIA-70', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (57, 'MARIA-70', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (58, 'MARIA-70', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (59, 'MARIA-70', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (60, 'MARIA-70', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (61, 'MARIA-70', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (62, 'MARIA-70', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (63, 'MARIA-70', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (64, 'MARIA-70', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (65, 'MARIA-70', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (66, 'MARIA-70', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (67, 'MARIA-70', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (68, 'MARIA-70', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (69, 'MARIA-110', 1, 'd_driver_km', 'Работа водителя', 300.0000, 'км', 15.00, 18.30, 5490.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (70, 'MARIA-110', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (71, 'MARIA-110', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (72, 'MARIA-110', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (73, 'MARIA-110', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (74, 'MARIA-110', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (75, 'MARIA-110', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (76, 'MARIA-110', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (77, 'MARIA-110', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (78, 'MARIA-110', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (79, 'MARIA-110', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (80, 'MARIA-110', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (81, 'MARIA-110', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (82, 'MARIA-110', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (83, 'MARIA-110', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (84, 'MARIA-110', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (85, 'MARIA-110', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (86, 'MARIA-130', 1, 'd_driver_km', 'Работа водителя', 300.0000, 'км', 15.00, 18.30, 5490.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (87, 'MARIA-130', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (88, 'MARIA-130', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (89, 'MARIA-130', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (90, 'MARIA-130', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (91, 'MARIA-130', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (92, 'MARIA-130', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (93, 'MARIA-130', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (94, 'MARIA-130', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (95, 'MARIA-130', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (96, 'MARIA-130', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (97, 'MARIA-130', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (98, 'MARIA-130', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (99, 'MARIA-130', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (100, 'MARIA-130', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (101, 'MARIA-130', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (102, 'MARIA-130', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (103, 'RUSLAN-10', 1, 'd_driver_km', 'Работа водителя', 1800.0000, 'км', 15.00, 18.30, 32940.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (104, 'RUSLAN-10', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (105, 'RUSLAN-10', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (106, 'RUSLAN-10', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (107, 'RUSLAN-10', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (108, 'RUSLAN-10', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (109, 'RUSLAN-10', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (110, 'RUSLAN-10', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (111, 'RUSLAN-10', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (112, 'RUSLAN-10', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (113, 'RUSLAN-10', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (114, 'RUSLAN-10', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (115, 'RUSLAN-10', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (116, 'RUSLAN-10', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (117, 'RUSLAN-10', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (118, 'RUSLAN-10', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (119, 'RUSLAN-10', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (120, 'RUSLAN-30', 1, 'd_driver_km', 'Работа водителя', 1800.0000, 'км', 15.00, 18.30, 32940.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (121, 'RUSLAN-30', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (122, 'RUSLAN-30', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (123, 'RUSLAN-30', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (124, 'RUSLAN-30', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (167, 'RUSLAN-90', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (125, 'RUSLAN-30', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (126, 'RUSLAN-30', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (127, 'RUSLAN-30', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (128, 'RUSLAN-30', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (129, 'RUSLAN-30', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (130, 'RUSLAN-30', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (131, 'RUSLAN-30', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (132, 'RUSLAN-30', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (133, 'RUSLAN-30', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (134, 'RUSLAN-30', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (135, 'RUSLAN-30', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (136, 'RUSLAN-30', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (137, 'RUSLAN-70', 1, 'd_driver_km', 'Работа водителя', 1800.0000, 'км', 15.00, 18.30, 32940.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (138, 'RUSLAN-70', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (139, 'RUSLAN-70', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (140, 'RUSLAN-70', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (141, 'RUSLAN-70', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (142, 'RUSLAN-70', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (143, 'RUSLAN-70', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (144, 'RUSLAN-70', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (145, 'RUSLAN-70', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (146, 'RUSLAN-70', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (147, 'RUSLAN-70', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (148, 'RUSLAN-70', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (149, 'RUSLAN-70', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (150, 'RUSLAN-70', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (151, 'RUSLAN-70', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (152, 'RUSLAN-70', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (153, 'RUSLAN-70', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (154, 'RUSLAN-90', 1, 'd_driver_km', 'Работа водителя', 1800.0000, 'км', 15.00, 18.30, 32940.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (155, 'RUSLAN-90', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (156, 'RUSLAN-90', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (157, 'RUSLAN-90', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (158, 'RUSLAN-90', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (159, 'RUSLAN-90', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (160, 'RUSLAN-90', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (161, 'RUSLAN-90', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (162, 'RUSLAN-90', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (163, 'RUSLAN-90', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (164, 'RUSLAN-90', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (165, 'RUSLAN-90', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (166, 'RUSLAN-90', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (168, 'RUSLAN-90', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (169, 'RUSLAN-90', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (170, 'RUSLAN-90', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (171, 'RUSLAN-110', 1, 'd_driver_km', 'Работа водителя', 1800.0000, 'км', 15.00, 18.30, 32940.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (172, 'RUSLAN-110', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (173, 'RUSLAN-110', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (174, 'RUSLAN-110', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (175, 'RUSLAN-110', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (176, 'RUSLAN-110', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (177, 'RUSLAN-110', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (178, 'RUSLAN-110', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (179, 'RUSLAN-110', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (180, 'RUSLAN-110', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (181, 'RUSLAN-110', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (182, 'RUSLAN-110', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (183, 'RUSLAN-110', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (184, 'RUSLAN-110', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (185, 'RUSLAN-110', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (186, 'RUSLAN-110', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (187, 'RUSLAN-110', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (188, 'RUSLAN-130', 1, 'd_driver_km', 'Работа водителя', 1800.0000, 'км', 15.00, 18.30, 32940.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (189, 'RUSLAN-130', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (190, 'RUSLAN-130', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (191, 'RUSLAN-130', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (192, 'RUSLAN-130', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (193, 'RUSLAN-130', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (194, 'RUSLAN-130', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (195, 'RUSLAN-130', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (196, 'RUSLAN-130', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (197, 'RUSLAN-130', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (198, 'RUSLAN-130', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (199, 'RUSLAN-130', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (200, 'RUSLAN-130', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (201, 'RUSLAN-130', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (202, 'RUSLAN-130', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (203, 'RUSLAN-130', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (204, 'RUSLAN-130', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (205, 'TIMUR-10', 1, 'd_driver_km', 'Работа водителя', 900.0000, 'км', 15.00, 18.30, 16470.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (206, 'TIMUR-10', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (207, 'TIMUR-10', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (208, 'TIMUR-10', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (209, 'TIMUR-10', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (210, 'TIMUR-10', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (211, 'TIMUR-10', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (212, 'TIMUR-10', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (213, 'TIMUR-10', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (214, 'TIMUR-10', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (215, 'TIMUR-10', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (216, 'TIMUR-10', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (217, 'TIMUR-10', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (218, 'TIMUR-10', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (219, 'TIMUR-10', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (220, 'TIMUR-10', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (221, 'TIMUR-10', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (222, 'TIMUR-30', 1, 'd_driver_km', 'Работа водителя', 900.0000, 'км', 15.00, 18.30, 16470.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (223, 'TIMUR-30', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (224, 'TIMUR-30', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (225, 'TIMUR-30', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (226, 'TIMUR-30', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (227, 'TIMUR-30', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (228, 'TIMUR-30', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (229, 'TIMUR-30', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (230, 'TIMUR-30', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (231, 'TIMUR-30', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (232, 'TIMUR-30', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (233, 'TIMUR-30', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (234, 'TIMUR-30', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (235, 'TIMUR-30', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (236, 'TIMUR-30', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (237, 'TIMUR-30', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (238, 'TIMUR-30', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (239, 'TIMUR-70', 1, 'd_driver_km', 'Работа водителя', 900.0000, 'км', 15.00, 18.30, 16470.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (240, 'TIMUR-70', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (241, 'TIMUR-70', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (242, 'TIMUR-70', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (243, 'TIMUR-70', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (244, 'TIMUR-70', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (245, 'TIMUR-70', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (246, 'TIMUR-70', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (247, 'TIMUR-70', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (248, 'TIMUR-70', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (249, 'TIMUR-70', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (250, 'TIMUR-70', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (251, 'TIMUR-70', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (252, 'TIMUR-70', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (253, 'TIMUR-70', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (254, 'TIMUR-70', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (255, 'TIMUR-70', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (256, 'TIMUR-90', 1, 'd_driver_km', 'Работа водителя', 900.0000, 'км', 15.00, 18.30, 16470.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (257, 'TIMUR-90', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (258, 'TIMUR-90', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (259, 'TIMUR-90', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (260, 'TIMUR-90', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (261, 'TIMUR-90', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (262, 'TIMUR-90', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (263, 'TIMUR-90', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (264, 'TIMUR-90', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (265, 'TIMUR-90', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (266, 'TIMUR-90', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (267, 'TIMUR-90', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (268, 'TIMUR-90', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (269, 'TIMUR-90', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (270, 'TIMUR-90', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (271, 'TIMUR-90', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (272, 'TIMUR-90', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (273, 'TIMUR-110', 1, 'd_driver_km', 'Работа водителя', 900.0000, 'км', 15.00, 18.30, 16470.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (274, 'TIMUR-110', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (275, 'TIMUR-110', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (276, 'TIMUR-110', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (277, 'TIMUR-110', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (278, 'TIMUR-110', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (279, 'TIMUR-110', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (280, 'TIMUR-110', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (281, 'TIMUR-110', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (282, 'TIMUR-110', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (283, 'TIMUR-110', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (284, 'TIMUR-110', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (285, 'TIMUR-110', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (286, 'TIMUR-110', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (287, 'TIMUR-110', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (288, 'TIMUR-110', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (289, 'TIMUR-110', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (290, 'TIMUR-130', 1, 'd_driver_km', 'Работа водителя', 900.0000, 'км', 15.00, 18.30, 16470.00, 'direct', 'f', 'Красная цена из настроек, синее количество у менеджера');
INSERT INTO "public"."demo_expenses" VALUES (291, 'TIMUR-130', 2, 'd_demo_work', 'Работа демонстратора', 16.0000, 'часы', 1350.00, 1647.00, 26352.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (292, 'TIMUR-130', 3, 'd_cryoblaster', 'Демонстрация криобластера', 5.0000, 'усл', 4000.00, 4880.00, 24400.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (293, 'TIMUR-130', 4, 'd_hard_conditions', 'Усложненные условия труда', 0.0000, 'усл', 1700.00, 2074.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (294, 'TIMUR-130', 5, 'd_electric_compressor', 'Ручная работа с кабелем и шланга компрессора', 0.0000, 'усл', 3500.00, 4270.00, 0.00, 'direct', 'f', 'Красная цена из настроек');
INSERT INTO "public"."demo_expenses" VALUES (295, 'TIMUR-130', 6, 'd_electro_reel', 'Использование электрокатушки', 1.0000, 'усл', 1500.00, 1830.00, 1830.00, 'direct', 'f', 'Синее поле, менеджер может менять количество и цену');
INSERT INTO "public"."demo_expenses" VALUES (296, 'TIMUR-130', 7, 'd_load_unload', 'Выгрузка и загрузка компрессора и электрокатушки', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (297, 'TIMUR-130', 8, 'legacy_payroll_tax', 'Налоги на ФОТ', 1.0000, 'усл', 12480.00, 15225.60, 15225.60, 'payroll_tax', 'f', 'Формула: 30% от строк ФОТ и демонстратора');
INSERT INTO "public"."demo_expenses" VALUES (298, 'TIMUR-130', 9, 'o_hotel_manager', 'Расходы на отель Менеджера', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (299, 'TIMUR-130', 10, 'o_hotel_driver', 'Расходы на отель Водителя', 3.0000, 'день х чел', 2800.00, 3416.00, 10248.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (300, 'TIMUR-130', 11, 'o_manager_travel', 'Расходы на переезд менеджера', 0.0000, 'усл', 3000.00, 3660.00, 0.00, 'direct', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (301, 'TIMUR-130', 12, 'o_toll', 'Расходы на платную дорогу', 0.0000, 'усл', 0.00, 0.00, 0.00, 'direct', 'f', 'Пользовательское значение');
INSERT INTO "public"."demo_expenses" VALUES (302, 'TIMUR-130', 13, 'o_per_diem', 'Суточные для командировки', 6.0000, 'день х чел', 1500.00, 1830.00, 10980.00, 'direct', 'f', 'Красное/формульное поле');
INSERT INTO "public"."demo_expenses" VALUES (303, 'TIMUR-130', 14, 'o_diesel', 'Расходы на дизель (12 л/100км), л', 0.0000, 'литры', 63.93, 78.00, 0.00, 'diesel', 'f', 'Формула: км / 100 × 12 × цена топлива');
INSERT INTO "public"."demo_expenses" VALUES (304, 'TIMUR-130', 15, 'o_gazelle_amort', 'Амортизация Газели', 0.0000, 'км', 8.20, 10.00, 0.00, 'gazelle_amort', 'f', 'Формула: км × ставка амортизации');
INSERT INTO "public"."demo_expenses" VALUES (305, 'TIMUR-130', 16, 'o_dry_ice_purchase', 'Расходы на закупку сухого льда', 300.0000, 'кг', 73.77, 90.00, 27000.00, 'direct_vat_price', 'f', 'Синее поле');
INSERT INTO "public"."demo_expenses" VALUES (306, 'TIMUR-130', 17, 'o_dry_ice_delivery', 'Расходы на доставку сухого льда в цех', 0.0000, 'усл', 1500.00, 1830.00, 0.00, 'direct', 'f', 'Красная цена из настроек');

-- ----------------------------
-- Table structure for products
-- ----------------------------
DROP TABLE IF EXISTS "public"."products";
CREATE TABLE "public"."products" (
  "product_id" text COLLATE "pg_catalog"."default" NOT NULL,
  "sku" text COLLATE "pg_catalog"."default" NOT NULL,
  "name" text COLLATE "pg_catalog"."default" NOT NULL,
  "price_vat" numeric(14,2) NOT NULL DEFAULT 0,
  "price_net" numeric(14,2) NOT NULL DEFAULT 0,
  "min_price_net" numeric(14,2) NOT NULL DEFAULT 0,
  "margin_pct" numeric(8,6) NOT NULL DEFAULT 0.65,
  "comment" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "row_order" int4 NOT NULL DEFAULT 0,
  "city_params" jsonb NOT NULL DEFAULT '{}'::jsonb
)
;

-- ----------------------------
-- Records of products
-- ----------------------------
INSERT INTO "public"."products" VALUES ('PRD-1777920080631', '3453', '345345', 453453.00, 45345.00, 0.00, 0.650000, '', 1, '{"Казань": {"mr": 9069.0, "pr": 4534.5, "st": 0.565}, "Москва": {"mr": 9069.0, "pr": 4534.5, "st": 0.465}}');
INSERT INTO "public"."products" VALUES ('BASIC-2.0-P10-PLa-F3500', 'BASIC-2.0-P10-PLa-F3500', 'Криобластер BASIC 2.0 (P10/PLa), 0-60 кг/ч, 3500 л/мин', 1169980.00, 959000.00, 0.00, 0.650000, 'Демо-товар', 2, '{"Казань": {"mr": 191800.0, "pr": 95900.0, "st": 0.565}, "Москва": {"mr": 191800.0, "pr": 95900.0, "st": 0.465}}');
INSERT INTO "public"."products" VALUES ('MINI-3.0-P10-F2500', 'MINI-3.0-P10-F2500', 'Криобластер MINI 3.0 (P10), 30 кг/ч, 2500 л/мин, MINI-II', 203740.00, 167000.00, 0.00, 0.650000, 'Демо-товар', 3, '{"Казань": {"mr": 33400.0, "pr": 16700.0, "st": 0.565}, "Москва": {"mr": 33400.0, "pr": 16700.0, "st": 0.465}}');
INSERT INTO "public"."products" VALUES ('NZ-LV-5000', 'NZ-LV-5000', 'Сопло агрессивное NZ-LV-5000', 92720.00, 76000.00, 0.00, 0.650000, 'Демо-товар', 4, '{"Казань": {"mr": 15200.0, "pr": 7600.0, "st": 0.565}, "Москва": {"mr": 15200.0, "pr": 7600.0, "st": 0.465}}');
INSERT INTO "public"."products" VALUES ('ONE-2.0-P12-PLa-F3500', 'ONE-2.0-P12-PLa-F3500', 'Криобластер ONE 2.0 (P12/PLa), 0-150 кг/ч, 3500 л/мин', 1886120.00, 1546000.00, 0.00, 0.650000, 'Демо-товар', 5, '{"Казань": {"mr": 309200.0, "pr": 154600.0, "st": 0.565}, "Москва": {"mr": 309200.0, "pr": 154600.0, "st": 0.465}}');
INSERT INTO "public"."products" VALUES ('TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'Криобластер TRANSFORMER 2.0 MAX (P12/PLa), 0-150 кг/ч, 3500 л/мин', 2166720.00, 1776000.00, 0.00, 0.650000, 'Демо-товар', 6, '{"Казань": {"mr": 355200.0, "pr": 177600.0, "st": 0.565}, "Москва": {"mr": 355200.0, "pr": 177600.0, "st": 0.465}}');

-- ----------------------------
-- Table structure for sale_rows
-- ----------------------------
DROP TABLE IF EXISTS "public"."sale_rows";
CREATE TABLE "public"."sale_rows" (
  "id" int8 NOT NULL DEFAULT nextval('sale_rows_id_seq'::regclass),
  "action_id" text COLLATE "pg_catalog"."default" NOT NULL,
  "row_order" int4 NOT NULL,
  "product_id" text COLLATE "pg_catalog"."default" NOT NULL,
  "sku" text COLLATE "pg_catalog"."default" NOT NULL,
  "name" text COLLATE "pg_catalog"."default" NOT NULL,
  "price_vat" numeric(14,2) NOT NULL DEFAULT 0,
  "price_net" numeric(14,2) NOT NULL DEFAULT 0,
  "qty" numeric(14,4) NOT NULL DEFAULT 1,
  "total_vat" numeric(14,2) NOT NULL DEFAULT 0,
  "total_net" numeric(14,2) NOT NULL DEFAULT 0,
  "vat_sum" numeric(14,2) NOT NULL DEFAULT 0,
  "min_price_net" numeric(14,2) NOT NULL DEFAULT 0,
  "margin_unit" numeric(14,2) NOT NULL DEFAULT 0,
  "margin_pct" numeric(8,6) NOT NULL DEFAULT 0.65,
  "bonus_net" numeric(14,2) NOT NULL DEFAULT 0,
  "pr0_vat" numeric(14,2) NOT NULL DEFAULT 0,
  "mr_unit" numeric(14,2) NOT NULL DEFAULT 0,
  "pr_unit" numeric(14,2) NOT NULL DEFAULT 0,
  "st_pct" numeric(8,6) NOT NULL DEFAULT 0,
  "cash_net" numeric(14,2) NOT NULL DEFAULT 0
)
;

-- ----------------------------
-- Records of sale_rows
-- ----------------------------
INSERT INTO "public"."sale_rows" VALUES (1, 'MARIA-20', 1, 'TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'Криобластер TRANSFORMER 2.0 MAX (P12/PLa), 0-150 кг/ч, 3500 л/мин', 2166720.00, 1776000.00, 1.0000, 2166720.00, 1776000.00, 390720.00, 0.00, 0.00, 0.650000, 0.00, 2166720.00, 355200.00, 177600.00, 0.565000, 200688.00);
INSERT INTO "public"."sale_rows" VALUES (2, 'MARIA-40', 1, 'MINI-3.0-P10-F2500', 'MINI-3.0-P10-F2500', 'Криобластер MINI 3.0 (P10), 30 кг/ч, 2500 л/мин, MINI-II', 203740.00, 167000.00, 1.0000, 203740.00, 167000.00, 36740.00, 0.00, 0.00, 0.650000, 0.00, 203740.00, 33400.00, 16700.00, 0.565000, 18871.00);
INSERT INTO "public"."sale_rows" VALUES (3, 'MARIA-50', 1, 'BASIC-2.0-P10-PLa-F3500', 'BASIC-2.0-P10-PLa-F3500', 'Криобластер BASIC 2.0 (P10/PLa), 0-60 кг/ч, 3500 л/мин', 1169980.00, 959000.00, 1.0000, 1169980.00, 959000.00, 210980.00, 0.00, 0.00, 0.650000, 0.00, 1169980.00, 191800.00, 95900.00, 0.565000, 108367.00);
INSERT INTO "public"."sale_rows" VALUES (4, 'MARIA-80', 1, 'NZ-LV-5000', 'NZ-LV-5000', 'Сопло агрессивное NZ-LV-5000', 92720.00, 76000.00, 2.0000, 185440.00, 152000.00, 33440.00, 0.00, 0.00, 0.650000, 0.00, 92720.00, 15200.00, 7600.00, 0.565000, 17176.00);
INSERT INTO "public"."sale_rows" VALUES (5, 'MARIA-100', 1, 'BASIC-2.0-P10-PLa-F3500', 'BASIC-2.0-P10-PLa-F3500', 'Криобластер BASIC 2.0 (P10/PLa), 0-60 кг/ч, 3500 л/мин', 1169980.00, 959000.00, 1.0000, 1169980.00, 959000.00, 210980.00, 0.00, 0.00, 0.650000, 0.00, 1169980.00, 191800.00, 95900.00, 0.565000, 108367.00);
INSERT INTO "public"."sale_rows" VALUES (6, 'MARIA-120', 1, 'TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'Криобластер TRANSFORMER 2.0 MAX (P12/PLa), 0-150 кг/ч, 3500 л/мин', 2166720.00, 1776000.00, 1.0000, 2166720.00, 1776000.00, 390720.00, 0.00, 0.00, 0.650000, 0.00, 2166720.00, 355200.00, 177600.00, 0.565000, 200688.00);
INSERT INTO "public"."sale_rows" VALUES (7, 'MARIA-140', 1, 'MINI-3.0-P10-F2500', 'MINI-3.0-P10-F2500', 'Криобластер MINI 3.0 (P10), 30 кг/ч, 2500 л/мин, MINI-II', 203740.00, 167000.00, 1.0000, 203740.00, 167000.00, 36740.00, 0.00, 0.00, 0.650000, 0.00, 203740.00, 33400.00, 16700.00, 0.565000, 18871.00);
INSERT INTO "public"."sale_rows" VALUES (8, 'RUSLAN-20', 1, 'BASIC-2.0-P10-PLa-F3500', 'BASIC-2.0-P10-PLa-F3500', 'Криобластер BASIC 2.0 (P10/PLa), 0-60 кг/ч, 3500 л/мин', 1169980.00, 959000.00, 1.0000, 1169980.00, 959000.00, 210980.00, 0.00, 0.00, 0.650000, 0.00, 1169980.00, 191800.00, 95900.00, 0.565000, 108367.00);
INSERT INTO "public"."sale_rows" VALUES (9, 'RUSLAN-40', 1, 'TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'Криобластер TRANSFORMER 2.0 MAX (P12/PLa), 0-150 кг/ч, 3500 л/мин', 2166720.00, 1776000.00, 1.0000, 2166720.00, 1776000.00, 390720.00, 0.00, 0.00, 0.650000, 0.00, 2166720.00, 355200.00, 177600.00, 0.565000, 200688.00);
INSERT INTO "public"."sale_rows" VALUES (10, 'RUSLAN-50', 1, 'NZ-LV-5000', 'NZ-LV-5000', 'Сопло агрессивное NZ-LV-5000', 92720.00, 76000.00, 2.0000, 185440.00, 152000.00, 33440.00, 0.00, 0.00, 0.650000, 0.00, 92720.00, 15200.00, 7600.00, 0.565000, 17176.00);
INSERT INTO "public"."sale_rows" VALUES (11, 'RUSLAN-80', 1, 'ONE-2.0-P12-PLa-F3500', 'ONE-2.0-P12-PLa-F3500', 'Криобластер ONE 2.0 (P12/PLa), 0-150 кг/ч, 3500 л/мин', 1886120.00, 1546000.00, 1.0000, 1886120.00, 1546000.00, 340120.00, 0.00, 0.00, 0.650000, 0.00, 1886120.00, 309200.00, 154600.00, 0.565000, 174698.00);
INSERT INTO "public"."sale_rows" VALUES (12, 'RUSLAN-100', 1, 'NZ-LV-5000', 'NZ-LV-5000', 'Сопло агрессивное NZ-LV-5000', 92720.00, 76000.00, 2.0000, 185440.00, 152000.00, 33440.00, 0.00, 0.00, 0.650000, 0.00, 92720.00, 15200.00, 7600.00, 0.565000, 17176.00);
INSERT INTO "public"."sale_rows" VALUES (13, 'RUSLAN-120', 1, 'BASIC-2.0-P10-PLa-F3500', 'BASIC-2.0-P10-PLa-F3500', 'Криобластер BASIC 2.0 (P10/PLa), 0-60 кг/ч, 3500 л/мин', 1169980.00, 959000.00, 1.0000, 1169980.00, 959000.00, 210980.00, 0.00, 0.00, 0.650000, 0.00, 1169980.00, 191800.00, 95900.00, 0.565000, 108367.00);
INSERT INTO "public"."sale_rows" VALUES (14, 'RUSLAN-140', 1, 'TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'Криобластер TRANSFORMER 2.0 MAX (P12/PLa), 0-150 кг/ч, 3500 л/мин', 2166720.00, 1776000.00, 1.0000, 2166720.00, 1776000.00, 390720.00, 0.00, 0.00, 0.650000, 0.00, 2166720.00, 355200.00, 177600.00, 0.565000, 200688.00);
INSERT INTO "public"."sale_rows" VALUES (15, 'TIMUR-20', 1, 'ONE-2.0-P12-PLa-F3500', 'ONE-2.0-P12-PLa-F3500', 'Криобластер ONE 2.0 (P12/PLa), 0-150 кг/ч, 3500 л/мин', 1886120.00, 1546000.00, 1.0000, 1886120.00, 1546000.00, 340120.00, 0.00, 0.00, 0.650000, 0.00, 1886120.00, 309200.00, 154600.00, 0.565000, 174698.00);
INSERT INTO "public"."sale_rows" VALUES (16, 'TIMUR-40', 1, 'NZ-LV-5000', 'NZ-LV-5000', 'Сопло агрессивное NZ-LV-5000', 92720.00, 76000.00, 2.0000, 185440.00, 152000.00, 33440.00, 0.00, 0.00, 0.650000, 0.00, 92720.00, 15200.00, 7600.00, 0.565000, 17176.00);
INSERT INTO "public"."sale_rows" VALUES (17, 'TIMUR-50', 1, 'MINI-3.0-P10-F2500', 'MINI-3.0-P10-F2500', 'Криобластер MINI 3.0 (P10), 30 кг/ч, 2500 л/мин, MINI-II', 203740.00, 167000.00, 1.0000, 203740.00, 167000.00, 36740.00, 0.00, 0.00, 0.650000, 0.00, 203740.00, 33400.00, 16700.00, 0.565000, 18871.00);
INSERT INTO "public"."sale_rows" VALUES (18, 'TIMUR-80', 1, 'TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'TR-2.0-MAX-P12-PLa-F3500-PRO-II', 'Криобластер TRANSFORMER 2.0 MAX (P12/PLa), 0-150 кг/ч, 3500 л/мин', 2166720.00, 1776000.00, 1.0000, 2166720.00, 1776000.00, 390720.00, 0.00, 0.00, 0.650000, 0.00, 2166720.00, 355200.00, 177600.00, 0.565000, 200688.00);
INSERT INTO "public"."sale_rows" VALUES (19, 'TIMUR-100', 1, 'MINI-3.0-P10-F2500', 'MINI-3.0-P10-F2500', 'Криобластер MINI 3.0 (P10), 30 кг/ч, 2500 л/мин, MINI-II', 203740.00, 167000.00, 1.0000, 203740.00, 167000.00, 36740.00, 0.00, 0.00, 0.650000, 0.00, 203740.00, 33400.00, 16700.00, 0.565000, 18871.00);
INSERT INTO "public"."sale_rows" VALUES (20, 'TIMUR-120', 1, 'ONE-2.0-P12-PLa-F3500', 'ONE-2.0-P12-PLa-F3500', 'Криобластер ONE 2.0 (P12/PLa), 0-150 кг/ч, 3500 л/мин', 1886120.00, 1546000.00, 1.0000, 1886120.00, 1546000.00, 340120.00, 0.00, 0.00, 0.650000, 0.00, 1886120.00, 309200.00, 154600.00, 0.565000, 174698.00);
INSERT INTO "public"."sale_rows" VALUES (21, 'TIMUR-140', 1, 'NZ-LV-5000', 'NZ-LV-5000', 'Сопло агрессивное NZ-LV-5000', 92720.00, 76000.00, 2.0000, 185440.00, 152000.00, 33440.00, 0.00, 0.00, 0.650000, 0.00, 92720.00, 15200.00, 7600.00, 0.565000, 17176.00);

-- ----------------------------
-- View structure for v_actions_with_lock
-- ----------------------------
DROP VIEW IF EXISTS "public"."v_actions_with_lock";
CREATE VIEW "public"."v_actions_with_lock" AS  SELECT action_id,
    action_type,
    manager_login,
    sequence_no,
    action_date,
    client,
    city,
    model,
    task_description,
    comment,
    is_director_confirmed,
    confirmed_amount,
    director_comment,
    created_at,
    updated_at,
    payload,
    (EXISTS ( SELECT 1
           FROM actions p
          WHERE p.manager_login = a.manager_login AND p.action_type = 'Выплата премии'::text AND p.is_director_confirmed = true AND p.sequence_no >= a.sequence_no)) AS is_locked
   FROM actions a;

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."demo_expenses_id_seq"
OWNED BY "public"."demo_expenses"."id";
SELECT setval('"public"."demo_expenses_id_seq"', 306, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."sale_rows_id_seq"
OWNED BY "public"."sale_rows"."id";
SELECT setval('"public"."sale_rows_id_seq"', 21, true);

-- ----------------------------
-- Uniques structure for table actions
-- ----------------------------
ALTER TABLE "public"."actions" ADD CONSTRAINT "actions_manager_login_sequence_no_key" UNIQUE ("manager_login", "sequence_no");

-- ----------------------------
-- Checks structure for table actions
-- ----------------------------
ALTER TABLE "public"."actions" ADD CONSTRAINT "actions_action_type_check" CHECK (action_type = ANY (ARRAY['Проведенная демонстрация'::text, 'Проданное оборудование'::text, 'Выплата премии'::text]));

-- ----------------------------
-- Primary Key structure for table actions
-- ----------------------------
ALTER TABLE "public"."actions" ADD CONSTRAINT "actions_pkey" PRIMARY KEY ("action_id");

-- ----------------------------
-- Primary Key structure for table app_settings
-- ----------------------------
ALTER TABLE "public"."app_settings" ADD CONSTRAINT "app_settings_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Checks structure for table app_users
-- ----------------------------
ALTER TABLE "public"."app_users" ADD CONSTRAINT "app_users_role_check" CHECK (role = ANY (ARRAY['director'::text, 'manager'::text]));

-- ----------------------------
-- Primary Key structure for table app_users
-- ----------------------------
ALTER TABLE "public"."app_users" ADD CONSTRAINT "app_users_pkey" PRIMARY KEY ("login");

-- ----------------------------
-- Primary Key structure for table demo_criterion_values
-- ----------------------------
ALTER TABLE "public"."demo_criterion_values" ADD CONSTRAINT "demo_criterion_values_pkey" PRIMARY KEY ("action_id", "criterion_code");

-- ----------------------------
-- Primary Key structure for table demo_expenses
-- ----------------------------
ALTER TABLE "public"."demo_expenses" ADD CONSTRAINT "demo_expenses_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table products
-- ----------------------------
ALTER TABLE "public"."products" ADD CONSTRAINT "products_pkey" PRIMARY KEY ("product_id");

-- ----------------------------
-- Primary Key structure for table sale_rows
-- ----------------------------
ALTER TABLE "public"."sale_rows" ADD CONSTRAINT "sale_rows_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table actions
-- ----------------------------
ALTER TABLE "public"."actions" ADD CONSTRAINT "actions_manager_login_fkey" FOREIGN KEY ("manager_login") REFERENCES "public"."app_users" ("login") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table demo_criterion_values
-- ----------------------------
ALTER TABLE "public"."demo_criterion_values" ADD CONSTRAINT "demo_criterion_values_action_id_fkey" FOREIGN KEY ("action_id") REFERENCES "public"."actions" ("action_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table demo_expenses
-- ----------------------------
ALTER TABLE "public"."demo_expenses" ADD CONSTRAINT "demo_expenses_action_id_fkey" FOREIGN KEY ("action_id") REFERENCES "public"."actions" ("action_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sale_rows
-- ----------------------------
ALTER TABLE "public"."sale_rows" ADD CONSTRAINT "sale_rows_action_id_fkey" FOREIGN KEY ("action_id") REFERENCES "public"."actions" ("action_id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."sale_rows" ADD CONSTRAINT "sale_rows_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "public"."products" ("product_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
