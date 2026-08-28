import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';

// Material Modules
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatMenuModule } from '@angular/material/menu';

import { TestCase } from '../../../core/models/test.model';

export interface TestCaseDialogData {
  mode: 'add' | 'edit';
  suiteName?: string;
  suites: string[];
  availableTags: string[];
  testCase?: TestCase;
}

@Component({
  selector: 'app-test-case-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatMenuModule
  ],
  templateUrl: './test-case-dialog.component.html',
  styleUrl: './test-case-dialog.component.scss'
})
export class TestCaseDialogComponent implements OnInit {
  form!: FormGroup;
  isEditMode: boolean;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<TestCaseDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: TestCaseDialogData
  ) {
    this.isEditMode = data.mode === 'edit';
  }

  ngOnInit(): void {
    const test = this.data.testCase;
    
    this.form = this.fb.group({
      suiteName: [
        { value: this.data.suiteName || test?.file_name || this.data.suites[0], disabled: this.isEditMode },
        [Validators.required]
      ],
      name: [test ? this.cleanTestName(test.name) : '', [Validators.required, Validators.minLength(3)]],
      documentation: [test?.documentation || '', [Validators.required]],
      tags: [test?.tags || ['custom'], [Validators.required]]
    });
  }

  private cleanTestName(fullName: string): string {
    return fullName.replace(/^TC-\d+\s*/, '');
  }

  onSubmit(): void {
    if (this.form.valid) {
      const rawValues = this.form.getRawValue();
      this.dialogRef.close({
        suiteName: rawValues.suiteName,
        data: {
          name: rawValues.name,
          documentation: rawValues.documentation,
          tags: rawValues.tags
        }
      });
    }
  }

  onReset(): void {
    this.form.reset();
  }

  onCancel(): void {
    this.dialogRef.close(null);
  }
}