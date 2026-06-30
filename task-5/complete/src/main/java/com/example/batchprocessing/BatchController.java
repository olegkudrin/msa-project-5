package com.example.batchprocessing;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.JobParametersInvalidException;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.repository.JobExecutionAlreadyRunningException;
import org.springframework.batch.core.repository.JobInstanceAlreadyCompleteException;
import org.springframework.batch.core.repository.JobRestartException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/batch")
public class BatchController {

    @Autowired
    private JobLauncher jobLauncher;

    @Autowired
    private Job importProductJob;

    @PostMapping("/run")
    public ResponseEntity<Map<String, String>> runJob() {
        Map<String, String> response = new HashMap<>();

        try {
            // Создаем уникальные параметры для каждого запуска
            JobParameters jobParameters = new JobParametersBuilder()
                    .addLong("startTime", System.currentTimeMillis())
                    .toJobParameters();

            // Запускаем job
            jobLauncher.run(importProductJob, jobParameters);

            response.put("status", "success");
            response.put("message", "Batch job started successfully");
            response.put("timestamp", String.valueOf(System.currentTimeMillis()));

            return ResponseEntity.ok(response);

        } catch (JobExecutionAlreadyRunningException e) {
            response.put("status", "error");
            response.put("message", "Job is already running");
            return ResponseEntity.status(HttpStatus.CONFLICT).body(response);

        } catch (JobRestartException e) {
            response.put("status", "error");
            response.put("message", "Job restart error: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);

        } catch (JobInstanceAlreadyCompleteException e) {
            response.put("status", "error");
            response.put("message", "Job instance already complete");
            return ResponseEntity.status(HttpStatus.CONFLICT).body(response);

        } catch (JobParametersInvalidException e) {
            response.put("status", "error");
            response.put("message", "Invalid job parameters: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);

        } catch (Exception e) {
            response.put("status", "error");
            response.put("message", "Unexpected error: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
}

