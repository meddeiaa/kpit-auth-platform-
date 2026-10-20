import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';

import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

import { TestManagementService } from '../../../core/services/test-management.service';

@Component({
  selector: 'app-test-case-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatTabsModule,
    MatProgressSpinnerModule,
    MatSnackBarModule
  ],
  templateUrl: './test-case-dialog.component.html',
  styleUrl: './test-case-dialog.component.scss'
})
export class TestCaseDialogComponent implements OnInit {
  isEditMode = false;

  /** Doit être bindé avec [(selectedIndex)] sur mat-tab-group */
  selectedTabIndex = 0;

  // Manual
  suiteName = '';
  testName = '';
  documentation = '';
  selectedTags: string[] = [];
  suites: string[] = [];
  availableTags: string[] = [];

  // AI Generator
  aiRequirement = '';
  isGenerating = false;
  isSavingAI = false;
  generatedCode = '';
  aiProvider = 'groq';
  aiTargetSuite = '';
  customSuiteName = '';
  aiTestName = 'TC-AI-01 Test Case';

  constructor(
    public dialogRef: MatDialogRef<TestCaseDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private testService: TestManagementService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.isEditMode = this.data?.mode === 'edit';
    this.suites = this.data?.suites || [];
    this.availableTags = this.data?.availableTags || [];
    this.suiteName = this.data?.suiteName || (this.suites.length ? this.suites[0] : '');

    // Initialisation de la suite cible pour la génération IA
    this.aiTargetSuite = this.suites.length ? this.suites[0] : 'NEW_SUITE';
    if (this.aiTargetSuite === 'NEW_SUITE') {
      this.customSuiteName = '03_ai_generated_tests.robot';
    }

    if (this.isEditMode && this.data?.testCase) {
      this.testName = this.data.testCase.name || '';
      this.documentation = this.data.testCase.documentation || '';
      this.selectedTags = [...(this.data.testCase.tags || [])];
      this.suiteName = this.data.testCase.file_name || this.suiteName;
    }
  }

  isValidManualForm(): boolean {
    return !!(this.testName && this.testName.trim() && this.suiteName);
  }

  onSaveManual(): void {
    if (!this.isValidManualForm()) return;
    this.dialogRef.close({
      type: 'manual',
      suiteName: this.suiteName,
      data: {
        name: this.testName.trim(),
        documentation: (this.documentation || '').trim(),
        tags: this.selectedTags
      }
    });
  }

  generateWithAI(): void {
  if (!this.aiRequirement || !this.aiRequirement.trim()) {
    this.snackBar.open('Veuillez saisir un besoin ou une fonctionnalité', 'Fermer', { duration: 3000 });
    return;
  }

  this.isGenerating = true;
  this.testService.generateTestWithAI(this.aiRequirement, this.aiTestName, this.aiTargetSuite).subscribe({
    next: (res) => {
      // Attribution à la vraie variable du composant : generatedCode
      this.generatedCode = res.generated_code || res.code;
      this.isGenerating = false;
      this.snackBar.open(`Script généré avec succès (${res.provider})`, 'Fermer', { duration: 3000 });
    },
    error: (err) => {
      this.isGenerating = false;
      this.snackBar.open('Erreur lors de la génération IA', 'Fermer', { duration: 3000 });
    }
  });
}

  onSaveAIGenerated(): void {
    if (!this.generatedCode || this.isSavingAI) return;

    this.isSavingAI = true;

    // Détermination du nom de fichier de suite de destination
    let targetFile = this.aiTargetSuite;
    if (this.aiTargetSuite === 'NEW_SUITE') {
      targetFile = (this.customSuiteName || '').trim() || '03_ai_generated_tests.robot';
    }
    if (!targetFile.endsWith('.robot')) {
      targetFile += '.robot';
    }

    this.testService.saveGeneratedTest(targetFile, this.generatedCode).subscribe({
      next: () => {
        this.isSavingAI = false;
        this.snackBar.open(`Saved to suite: ${targetFile}`, 'Close', {
          duration: 3500,
          panelClass: ['snackbar-success']
        });
        // Type ai_saved → le composant parent appelle loadTests()
        this.dialogRef.close({ type: 'ai_saved', filename: targetFile });
      },
      error: (err) => {
        this.isSavingAI = false;
        const msg = err?.error?.message || 'Failed to save generated script.';
        this.snackBar.open(msg, 'Close', {
          duration: 5000,
          panelClass: ['snackbar-error']
        });
      }
    });
  }

  clearAI(): void {
    this.aiRequirement = '';
    this.generatedCode = '';
    this.aiProvider = 'groq';
    this.aiTestName = 'TC-AI-01 Test Case';
  }

  copyCode(): void {
    if (!this.generatedCode) return;
    navigator.clipboard.writeText(this.generatedCode).then(() => {
      this.snackBar.open('Script copied to clipboard', 'Close', { duration: 2000 });
    });
  }
}