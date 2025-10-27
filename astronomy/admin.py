# astronomy/admin.py
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import (
    CelestialObjects, 
    ObservationLog, 
    AstroPhoto,
    EclipseObservation,
    ResearchProject,
    ResearchDataEntry,
    ResearchAnalysis,
    ResearchTemplate
)

class EclipseObservationForm(forms.ModelForm):
    class Meta:
        model = EclipseObservation
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        eclipse_type = cleaned_data.get('eclipse_type')
        safety_equipment = cleaned_data.get('safety_equipment')
        danjon_scale = cleaned_data.get('danjon_scale')
        
        #Critical : validate solar eclipse safety
        if eclipse_type and eclipse_type.startswith('solar_'):
            if not safety_equipment:
                raise forms.ValidationError(
                    "⚠️ SAFETY EQUIPMENT MUST BE SPECIFIED FOR SOLAR ECLIPSE! "
                    "Never observe the sun without proper protection!"
                )
        
        if danjon_scale and danjon_scale != '':
            if eclipse_type != 'lunar_total':
                raise forms.ValidationError(
                    "Danjon Scale is only applicable for Total Lunar Eclipses. "
                    f"Current eclipse type: {eclipse_type}"
                )
        
        return cleaned_data

class EclipseInline(admin.StackedInline):
    model = EclipseObservation
    form = EclipseObservationForm
    extra = 0
    max_num = 1
    
    fieldsets = (
        ('Eclipse type & Safety', {
            'fields': ('eclipse_type','safety_equipment'),
            'description':'⚠️ WARNING: Solar observation requires proper safety equipment!'
        }),
        ('Contact Times - Solar',{
            # FIX: Ganti ci_time menjadi c1_time
            'fields':('c1_time', 'c2_time', 'max_time', 'c3_time', 'c4_time'),
            'classes':('collapse',)
        }),
        ('Contact Times - Lunar',{
            'fields':('p1_time','u1_time','u2_time','u3_time','u4_time','p2_time'),
            'classes':('collapse',)
        }),
        ('Measurements',{
            # FIX: Hapus danjon_scale karena tidak ada di model
            'fields': ('magnitude', 'obscuration', 'duration_seconds', 'danjon_scale'),
            'classes':('collapse',)
        }),
        ('Phenomena Observed', {
            'fields':(
                # FIX: Ganti shadown_bands_notes menjadi shadow_bands_notes
                # FIX: Ganti baileys_beads_observed menjadi bailes_beads_observed
                'shadow_bands_observed', 'shadow_bands_notes',
                'bailes_beads_observed', 'diamond_ring_observed',
                'corona_shape', 'prominences_observed', 'prominences_notes'
            ),
            'classes':('collapse',)
        }),
        ('Environmental', {
            # FIX: Ganti temperature_drop menjadi temperatur_drop
            # FIX: Ganti animal_behaviour_notes menjadi animal_behaviour_notes (sesuai model)
            'fields':('temperatur_drop', 'animal_behaviour_notes', 'weather_impact'),
            'classes':('collapse',)
        })
    )

class AstroPhotoForm(forms.ModelForm):
    class Meta:
        model = AstroPhoto
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        eclipse_phase = cleaned_data.get('eclipse_phase')
        solar_photo_method = cleaned_data.get('solar_photo_method')
        
        # Validate solar photography safety
        if eclipse_phase and eclipse_phase.startswith('solar_'):
            # Skip validation for totality corona shots
            safe_phases = ['solar_corona', 'solar_prominence', 'solar_max']
            if eclipse_phase not in safe_phases and not solar_photo_method:
                raise forms.ValidationError(
                    "⚠️ SOLAR PHOTOGRAPHY METHOD MUST BE SPECIFIED! "
                    "Ensure proper solar filter is used!"
                )
        
        return cleaned_data

class AstroPhotoInline(admin.TabularInline):
    model = AstroPhoto
    form = AstroPhotoForm
    extra = 1
    fields = [
        'title', 'image', 'eclipse_phase', 
        'solar_photo_method', 'exact_time', 'capture_date',
        'exposure_time', 'iso', 'frames'
    ]
    
    def get_fields(self, request, obj=None):
        """Dynamic fields based on eclipse type"""
        if obj and hasattr(obj, 'eclipse_data'):
            if obj.eclipse_data.is_solar():
                return ['title', 'image', 'eclipse_phase', 'solar_photo_method', 
                       'filter_used', 'exact_time', 'exposure_time', 'iso']
            elif obj.eclipse_data.is_lunar():
                return ['title', 'image', 'eclipse_phase', 'exact_time', 
                       'exposure_time', 'iso', 'frames']
        return super().get_fields(request, obj)

class ResearchDataEntryInline(admin.TabularInline):
    model= ResearchDataEntry
    extra = 1
    fields = ['observation_datetime', 'days_from_start', 'data', 'data_quality', 'notes' ]
    readonly_fields = ['days_from_start']
    
class ResearchAnalysisInline(admin.StackedInline):
    model = ResearchAnalysis
    extra = 0
    fields = ['analysis_type', 'title', 'results', 'quality_rating', 'methodology']
    
    
# Register your models here.
@admin.register(CelestialObjects)
class CelestialObjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'object_type', 'constellation', 'magnitude', 'parent_object']
    list_filter = ['object_type']
    search_fields = ['name', 'constellation']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'object_type', 'constellation', 'magnitude')
        }),
        ('Physical Properties', {
            'fields': ('distance_ly', 'description')
        }),
        ('Orbital Data (for satellites)', {
            'fields': ('parent_object', 'orbital_period', 'semi_major_axis'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ObservationLog)
class ObservationLogAdmin(admin.ModelAdmin):
    inlines = [EclipseInline, AstroPhotoInline]
    list_display = ['title', 'object_name', 'observation_date', 'location', 'seeing'
                    , 'research_project', 'is_public']
    list_filter = ['seeing', 'research_project', 'is_public', 'observation_date']
    search_fields = ['title', 'object_name', 'notes']
    date_hierarchy = 'observation_date'
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'observation_date', 'research_project')
        }),
        ('Target Object', {
            'fields': ('celestial_object', 'object_name')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Conditions', {
            'fields': ('seeing', 'transparency', 'cloud_cover', 'temperature', 'moon_phase')
        }),
        ('Equipment', {
            'fields': ('telescope', 'eyepiece', 'magnification', 'camera'),
            'classes': ('collapse',)
        }),
        ('Observation Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('is_public', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def seeing_display(self,obj):
        colors = {5:'green', 4:'lightgreen', 3:'yellow', 2:'orange', 1:'red'}
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.seeing, 'gray'),
            obj.get_seeing_display()
        )
    
    seeing_display.short_description = 'Seeing'

@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'research_type', 'status', 'start_date', 'end_date',
                    'progress_bar', 'observation_count', 'data_count']
    list_filter = ['research_type', 'status', 'start_date']
    search_fields = ['title', 'description', 'hypothesis']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    
    inlines = [ResearchDataEntryInline, ResearchAnalysisInline]
    
    fieldsets = (
        ('Project Information', {
            'fields': ('title', 'slug', 'research_type', 'description', 'status')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'target_duration_days')
        }),
        ('Research Design', {
            'fields': ('hypothesis', 'expected_results', 'data_template'),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('actual_results', 'conclusions'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_public', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def progress_bar(self, obj):
        progress = obj.get_progress_percentage()
        if progress is None:
            return 'Ongoing'
        color = 'green' if progress >= 75 else 'orange' if progress >= 50 else 'red'
        return format_html(
            '<div style="width:100px; background-color:#f0f0f0;">'
            '<div style="width:{}px; background-color:{}; height:20px;"></div>'
            '</div>{}%',
            progress, color, progress
        )
    
    progress_bar.short_description = 'Progress'
    
    def observation_count(self, obj):
        count = obj.get_observation_count()
        return format_html(
            '<strong>{}</strong> observations', 
            count
        )
    observation_count.short_description = 'Observations'
    
    def data_count(self,obj):
        count = obj.get_data_entry_count()
        return format_html('<strong>{}</strong> data points', count)
    data_count.short_description = 'Data'
    
@admin.register(ResearchDataEntry)
class ResearchDataEntryAdmin(admin.ModelAdmin):
    list_display = ['project', 'observation_datetime', 'days_from_start',
                    'data_quality', 'is_validated', 'is_outlier']
    list_filter = ['project', 'data_quality', 'is_validated', 'is_outlier']
    search_fields =['project__title', 'notes']
    date_hierarchy = 'observation_datetime'
    
    fieldsets = (
        ('Project Link', {
            'fields': ('project', 'observation')
        }),
        ('Timing', {
            'fields': ('observation_datetime', 'days_from_start')
        }),
        ('Data', {
            'fields': ('data', 'data_quality', 'notes')
        }),
        ('Validation', {
            'fields': ('is_validated', 'is_outlier'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['days_from_start']

@admin.register(ResearchAnalysis)
class ResearchAnalysisAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'analysis_type', 'quality_rating', 'created_at']
    list_filter = ['analysis_type', 'quality_rating', 'project']
    search_fields = ['title', 'project__title']
    
    fieldsets = (
        ('Analysis Information', {
            'fields': ('project', 'analysis_type', 'title')
        }),
        ('Results', {
            'fields': ('results', 'theoretical_values', 'error_percentage', 'quality_rating')
        }),
        ('Documentation', {
            'fields': ('methodology', 'interpretation')
        }),
    )
    
    readonly_fields = ['created_at']
    
@admin.register(AstroPhoto)
class AstroPhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'object_name', 'capture_date', 'is_featured', 'thumbnail',
                    'celestial_objects', 'research_project', 'is_processed', 'is_public']
    list_filter = ['is_featured', 'capture_date', 'is_public', 'eclipse_phase', 'research_project']
    search_fields = ['title', 'description']
    date_hierarchy = 'capture_date'
    list_editable = ['is_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'image', 'capture_date', 'description')
        }),
        ('Links', {
            'fields': ('observation', 'celestial_objects', 'research_project')
        }),
        ('Technical Data', {
            'fields': ('exposure_time', 'iso', 'aperture', 'focal_length'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('is_processed', 'processing_notes', 'stacked_frames'),
            'classes': ('collapse',)
        }),
        ('Research Data', {
            'fields': ('sequence_number', 'eclipse_phase'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_public',),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail(self,obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />',obj.image.url)
        return "No image"
    thumbnail.short_description = 'Preview'
    
@admin.register(ResearchTemplate)
class ResearchTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'research_type', 'is_active']
    list_filter = ['research_type', 'is_active']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'research_type', 'description')
        }),
        ('Configuration', {
            'fields': ('template_config',),
            'description': 'JSON configuration for data fields and analysis'
        }),
        ('Instruction', {
            'fields': ('instruction',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    

@admin.action(description="Mark selected as validated")
def mark_as_validated(modeladmin, request, queryset):
    queryset.update(is_validated=True)

@admin.action(description="Mark selected as outliers")
def mark_as_outliers(modeladmin, request, queryset):
    queryset.update(is_outlier=True)

ResearchDataEntryAdmin.actions = [mark_as_validated, mark_as_outliers]

class AstronomyAdminSite(admin.AdminSite):
    site_header = "Astronomy Research Administration"
    site_title = "Astronomy Research"
    index_title = "Welcome to Astronomy Research Portal"

# Uncomment to use custom admin site
# astronomy_admin_site = AstronomyAdminSite(name='astronomy_admin')
# astronomy_admin_site.register(CelestialObjects, CelestialObjectsAdmin)
# ... register other models
    

