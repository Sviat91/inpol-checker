// 1. Кнопка "Umów wizytę w urzędzie"
button[<h3 _ngcontent-rnh-c237="">Cases.MakeAppointmentAtOffice</h3>]



// 2. Dropdown "Wybierz lokalizacje" (выбор адреса)
[<mat-select _ngcontent-rnh-c182="" role="combobox" aria-autocomplete="none" aria-haspopup="true" name="location" class="mat-select ng-tns-c115-1 ng-tns-c53-0 ng-valid ng-star-inserted ng-touched ng-dirty" aria-labelledby="mat-form-field-label-1 mat-select-value-1" id="mat-select-0" tabindex="0" aria-expanded="false" aria-required="false" aria-disabled="false" aria-invalid="false"><div cdk-overlay-origin="" class="mat-select-trigger ng-tns-c115-1"><div class="mat-select-value ng-tns-c115-1" id="mat-select-value-1"><!----><span class="mat-select-value-text ng-tns-c115-1 ng-star-inserted"><span class="ng-tns-c115-1 ng-star-inserted">ul. Marszałkowska 3/5, 00-624 Warszawa</span><!----><!----></span><!----></div><div class="mat-select-arrow-wrapper ng-tns-c115-1"><div class="mat-select-arrow ng-tns-c115-1"></div></div></div><!----></mat-select>]




// 3. Пункты адресов внутри (все 3 варианта)
[<span class="mat-option-text"> Al. Jerozolimskie 28, 00-024 Warszawa </span>
<span class="mat-option-text"> pl. Bankowy 3/5 00-950 Warszawa </span>
<span class="mat-option-text"> ul. Marszałkowska 3/5, 00-624 Warszawa </span>]



// 4. Dropdown "Wybierz kolejke" (выбор очереди)

[<mat-select _ngcontent-rnh-c182="" role="combobox" aria-autocomplete="none" aria-haspopup="true" name="queueName" panelclass="full-width-select" class="mat-select ng-tns-c115-3 ng-tns-c53-2 ng-valid ng-star-inserted ng-touched ng-dirty" aria-labelledby="mat-form-field-label-3 mat-select-value-3" id="mat-select-2" tabindex="0" aria-expanded="false" aria-required="false" aria-disabled="false" aria-invalid="false"><div cdk-overlay-origin="" class="mat-select-trigger ng-tns-c115-3"><div class="mat-select-value ng-tns-c115-3" id="mat-select-value-3"><!----><span class="mat-select-value-text ng-tns-c115-3 ng-star-inserted"><span class="ng-tns-c115-3 ng-star-inserted">X - applications for TEMPORARY STAY</span><!----><!----></span><!----></div><div class="mat-select-arrow-wrapper ng-tns-c115-3"><div class="mat-select-arrow ng-tns-c115-3"></div></div></div><!----></mat-select>]

// 5. Пункт "X - applications for TE..."
[<span class="mat-option-text"> X - applications for TEMPORARY STAY   </span>]

// 6. Календарь - кликабельная дата
CALENDAR_DATES =[<div class="mat-calendar-body-cell-content mat-focus-indicator"> 17 </div>]  # все даты для клика
ACTIVE_DATE =[<div class="mat-calendar-body-cell-content mat-focus-indicator mat-calendar-body-selected"> 17 </div>]  # текущая выбранная (для логов)

// 7. Слоты времени (когда появятся)
[будет потом]
SLOTS_CONTAINER =[<div _ngcontent-rnh-c182="" class="col-lg-6"><div _ngcontent-rnh-c182="" class="reservation__hours"><!----><div _ngcontent-rnh-c182="" class="tiles tiles--hours"><div _ngcontent-rnh-c182="" class="row"><!----></div></div></div></div>]
