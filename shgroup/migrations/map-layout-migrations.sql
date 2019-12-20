CREATE TABLE "shgroup_mymaplayout" ("id" serial NOT NULL PRIMARY KEY, "layout_json" jsonb NOT NULL, "project_id" integer NOT NULL);
CREATE TABLE "shgroup_projectmaplayout" ("id" serial NOT NULL PRIMARY KEY, "layout_json" jsonb NOT NULL, "project_id" integer NOT NULL);
-- Add field projectUser to projectmaplayout
ALTER TABLE "shgroup_projectmaplayout" ADD COLUMN "projectUser_id" integer NOT NULL;
-- Add field projectUser to mymaplayout
ALTER TABLE "shgroup_mymaplayout" ADD COLUMN "projectUser_id" integer NOT NULL;
-- Alter unique_together for projectmaplayout (1 constraint(s))
ALTER TABLE "shgroup_projectmaplayout" ADD CONSTRAINT "shgroup_projectmaplayout_projectUser_id_project_i_ddc0f66e_uniq" UNIQUE ("projectUser_id", "project_id");
-- Alter unique_together for mymaplayout (1 constraint(s))
ALTER TABLE "shgroup_mymaplayout" ADD CONSTRAINT "shgroup_mymaplayout_projectUser_id_project_id_7a558ce8_uniq" UNIQUE ("projectUser_id", "project_id");
ALTER TABLE "shgroup_mymaplayout" ADD CONSTRAINT "shgroup_mymaplayout_project_id_e4f4f5a1_fk_survey_project_id" FOREIGN KEY ("project_id") REFERENCES "survey_project" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "shgroup_mymaplayout_project_id_e4f4f5a1" ON "shgroup_mymaplayout" ("project_id");
ALTER TABLE "shgroup_projectmaplayout" ADD CONSTRAINT "shgroup_projectmapla_project_id_0dac755e_fk_survey_pr" FOREIGN KEY ("project_id") REFERENCES "survey_project" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "shgroup_projectmaplayout_project_id_0dac755e" ON "shgroup_projectmaplayout" ("project_id");
CREATE INDEX "shgroup_projectmaplayout_projectUser_id_95492257" ON "shgroup_projectmaplayout" ("projectUser_id");
ALTER TABLE "shgroup_projectmaplayout" ADD CONSTRAINT "shgroup_projectmapla_projectUser_id_95492257_fk_shgroup_p" FOREIGN KEY ("projectUser_id") REFERENCES "shgroup_projectuser" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "shgroup_mymaplayout_projectUser_id_68cbc497" ON "shgroup_mymaplayout" ("projectUser_id");
ALTER TABLE "shgroup_mymaplayout" ADD CONSTRAINT "shgroup_mymaplayout_projectUser_id_68cbc497_fk_shgroup_p" FOREIGN KEY ("projectUser_id") REFERENCES "shgroup_projectuser" ("id") DEFERRABLE INITIALLY DEFERRED;
-- Grant access to new tables
GRANT ALL ON DATABASE pulse TO fullstack412;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fullstack412;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO fullstack412;
