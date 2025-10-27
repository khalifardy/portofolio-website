# astronomy/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json

# Create your models here.
class CelestialObjects(models.Model):
    """Types of celestial objects.

    This model contains the list of celestial objects and their properties.
    """
    
    OBJECT_TYPES = [
        ('planet', 'Planet'),
        ('star', 'Star'),
        ('galaxy','Galaxy'),
        ('nebula', 'Nebula'),
        ('cluster', 'Star Cluster'),
        ('moon', 'Moon'),
        ('satellite', 'Planetary Satellite'),
        ('comet', 'Comet'),
        ('asteroid', 'Asteroid'),
        ('other', 'Other')
    ]
    
    name = models.CharField(max_length=100)
    """The name of the celestial object."""
    
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    """The type of the celestial object."""
    
    constellation = models.CharField(max_length=100, blank=True)
    """The constellation that the celestial object is in."""
    
    distance_ly = models.CharField(max_length=100, blank=True, 
                                   help_text='Distance in light years')
    """The distance to the celestial object in light years."""
    
    magnitude = models.CharField(max_length=20, blank=True)
    """The magnitude of the celestial object."""
    
    description = models.TextField()
    """A description of the celestial object."""
    
    parent_object = models.ForeignKey('self', on_delete=models.SET_NULL, 
                                      null=True, blank=True, help_text = "For satellites, parent planet")
    
    orbital_period = models.FloatField(null=True, blank=True, help_text="Days")
    
    semi_major_axis = models.FloatField(null=True, blank=True, help_text="km")
    
    class Meta:
        verbose_name_plural = 'Celestial Objects'
    def __str__(self):
        return self.name

class ObservationLog(models.Model):
    """
    Astronomy observation logs.

    This model contains the information about the observations of celestial objects.
    """
    
    SEEING_CONDITIONS = [
        (5, 'Excellent'),
        (4, 'Good'),
        (3, 'Average'),
        (2, 'Poor'),
        (1, 'Terrible')
    ]
    
    
    
    title = models.CharField(max_length=200)
    """
    The title of the observation log.
    """
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    """
    A slug of the observation log.
    """
    observation_date = models.DateTimeField()
    """
    The date of the observation.
    """
    
    # object observed
    celestial_object = models.ForeignKey(CelestialObjects, on_delete=models.SET_NULL, null=True, blank =True)
    """
    The celestial object that was observed.
    """
    object_name = models.CharField(max_length=100)
    """
    The name of the celestial object.
    """
    
    # location
    location = models.CharField(max_length=200)
    """
    The location of the observation.
    """
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    """
    The latitude of the observation.
    """
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    """
    The longitude of the observation.
    """
    
    # Conditions
    seeing = models.IntegerField(choices=SEEING_CONDITIONS)
    """
    The seeing conditions of the observation.
    """
    transparency = models.IntegerField(choices=SEEING_CONDITIONS)
    """
    The transparency of the sky during the observation.
    """
    moon_phase = models.CharField(max_length=50, blank=True)
    """
    The phase of the moon during the observation.
    """
    temperature = models.IntegerField(null=True, blank=True, help_text='Celsius')
    """
    The temperature during the observation.
    """
    cloud_cover = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                      help_text = "Percentage of 0-100")
    
    # Equipment
    telescope = models.CharField(max_length=100, blank=True)
    """
    The telescope used for the observation.
    """
    eyepiece = models.CharField(max_length=100, blank=True)
    """
    The eyepiece used for the observation.
    """
    magnification = models.CharField(max_length=50, blank=True)
    """
    The magnification used for the observation.
    """
    camera = models.CharField(max_length=100, blank=True)
    """
    The camera used for the observation.
    """
    
    # Notes
    notes = models.TextField()
    """
    The notes of the observation.
    """
    
    research_project = models.ForeignKey('ResearchProject', on_delete=models.SET_NULL, 
                                         null=True, blank=True, related_name='observation')
    
    # meta data
    is_public = models.BooleanField(default=True)
    """
    Whether the observation log is public or not.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    """
    The date the observation log was created.
    """
    updated_at = models.DateTimeField(auto_now=True)
    """
    The date the observation log was last updated.
    """
    
    class Meta:
        ordering = ['-observation_date']
        """
        The observations are ordered by the observation date.
        """
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.observation_date.strftime('%Y%m%d')}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.observation_date.strftime('%Y-%m-%d')}"

class ResearchProject(models.Model):
    """Container for research projects - supports multipke research types"""
    
    RESEARCH_TYPES = [
        ('orbital', 'Orbital Period Measurement'),
        ('variable_star', 'Variabe Star Observation'),
        ('meteor', 'Meteor Shower Study'),
        ('eclipse', 'Eclipse Documentation'),
        ('planetary', 'Planetary Observation'),
        ('deep_sky', 'Deep Sky Observation'),
        ('occultation', 'Occultation Timing'),
        ('sunspot','Sunspot Monitoring'),
        ('custom', 'Custom Research'),
    ]
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    research_type = models.CharField(max_length=20, choices=RESEARCH_TYPES)
    description = models.TextField()
    
    #Timeline
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    target_duration_days = models.IntegerField(help_text='Planned duration in days')
    
    #status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    
    #Goals & Hypothesis
    hypothesis = models.TextField(blank=True, help_text="What you want to prove/measure")
    expected_results = models.TextField(blank=True)
    
    #Results
    actual_results = models.TextField(blank=True)
    conclusions = models.TextField(blank=True)
    
    # Data template - stores the structure of data to collect
    # JSON format allows flexible schema per research type
    
    data_template = models.JSONField(default=dict,blank=True,
                                     help_text="Template for data collection fields")
    
    #Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_observation_count(self):
        return self.observation.count() 
    
    def get_data_entry_count(self):
        return self.data_entries.count()
    
    def get_progress_percentage(self):
        """Calculate progress based on dates"""
        
        if not self.end_date:
            return None
        
        from datetime import date
        total_days = (self.end_date - self.start_date).days
        elapsed_days = (date.today() - self.start_date).days
        return min(100, int((elapsed_days / total_days) * 100))
    
    def __str__(self):
        return f"{self.title} - {self.get_research_type_display()}"
    
class ResearchDataEntry(models.Model):
    """Flexible data entry for research - stores measurements & Observations"""
    
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE,
                                 related_name='data_entries')
    
    observation = models.ForeignKey(ObservationLog, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='research_data')
    
    observation_datetime = models.DateTimeField()
    days_from_start = models.FloatField(editable=False,
                                        help_text="Auto-calculated from project start")
    
    
    # Flexible data storage
    # For Jupiter moons: {"io": 2.3, "europa": -1.5, "ganymede": 4.1, "callisto": 8.2}
    # For variable stars: {"magnitude": 3.2, "comparison_star": "ref_1"}
    # For meteors: {"count": 15, "sporadic": 3, "fireballs": 1}
    
    data = models.JSONField(help_text="Flexible data storage")
    
    #quality indicator
    data_quality = models.IntegerField(choices=ObservationLog.SEEING_CONDITIONS,
                                       null=True,blank=True)
    
    notes = models.TextField(blank=True)
    
    #flags
    is_outlier = models.BooleanField(default=False, help_text = "Mark as statistical outlier")
    is_validated = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['observation_datetime']
        verbose_name_plural = "Research Data Entries"
        
    def save(self, *args, **kwargs):
        if self.project and self.observation_datetime:
            delta = self.observation_datetime.date() - self.project.start_date
            self.days_from_start = delta.days + (self.observation_datetime.hour/24.0)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.project.title} - Day {self.days_from_start:.2f}"
    

class ResearchAnalysis(models.Model):
    """Store analysis results for a research project"""
    
    ANALYSIS_TYPES = [
        ('period', 'Orbital Period Calculation'),
        ('kepler', "Kepler's Law Verification"),
        ('light_curve', 'Light Curve Analysis'),
        ('statistics', 'Statistical Analysis'),
        ('custom', 'Custom Analysis'),
    ]
    
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE,
                                related_name='analyses')
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    title = models.CharField(max_length=200)
    
    # Results storage
    # For orbital period: {"io": 1.77, "europa": 3.52, "ganymede": 7.12, "callisto": 16.5}
    # For Kepler: {"ratio_io": 0.0417, "ratio_europa": 0.0415, "average": 0.0416}
    
    results = models.JSONField()
    
    #comparison with theoretical values
    theoretical_values = models.JSONField(null=True,blank=True)
    error_percentage = models.JSONField(null=True,blank=True)
    
    #Qualitu assesment
    quality_rating = models.CharField(max_length=20, choices=[
        ('excellent', 'Excellent (<2% error)'),
        ('good', 'Good (2-5% error)'),
        ('fair', 'Fair (5-10% error)'),
        ('poor', 'Poor (>10% error)'),
    ], null = True, blank=True)
    
    #notes
    methodology = models.TextField(help_text="How the analysis was performed")
    interpretation = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Research Analysis"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.project.title}"

class AstroPhoto(models.Model):
    """
    Astrophotography images
    """
    ECLIPSE_PHASES = [
        # General
        ('', 'Not Eclipse/Regular'),
        ('pre', 'Pre-Eclipse'),
        ('post', 'Post-Eclipse'),
        
        # Lunar Eclipse Phases
        ('lunar_p1', 'Lunar - Penumbral Start'),
        ('lunar_u1', 'Lunar - Partial Start'),
        ('lunar_u2', 'Lunar - Total Start'),
        ('lunar_max', 'Lunar - Maximum'),
        ('lunar_u3', 'Lunar - Total End'),
        ('lunar_u4', 'Lunar - Partial End'),
        ('lunar_p2', 'Lunar - Penumbral End'),
        
        # Solar Eclipse Phases
        ('solar_c1', 'Solar - First Contact'),
        ('solar_c2', 'Solar - Second Contact (Total/Annular Start)'),
        ('solar_max', 'Solar - Maximum'),
        ('solar_c3', 'Solar - Third Contact (Total/Annular End)'),
        ('solar_c4', 'Solar - Fourth Contact'),
        
        # Solar Special Moments
        ('solar_diamond1', 'Solar - First Diamond Ring'),
        ('solar_diamond2', 'Solar - Second Diamond Ring'),
        ('solar_baileys', 'Solar - Baileys Beads'),
        ('solar_chromosphere', 'Solar - Chromosphere'),
        ('solar_corona', 'Solar - Corona (Totality)'),
        ('solar_prominence', 'Solar - Prominences'),
        ('solar_shadow_bands', 'Solar - Shadow Bands'),
        
        # Composite/Special
        ('composite', 'Composite/Montage'),
        ('sequence', 'Time Sequence'),
    ]
     
    eclipse_phase = models.CharField(
         max_length=20,
         choices=ECLIPSE_PHASES,
         blank=True,
         help_text="Phase of eclipse when photo taken "
    )
     
     # Safety info for solar photos
    SOLAR_PHOTO_METHOD = [
        ('', 'N/A'),
        ('direct_filtered', 'Direct with Solar Filter'),
        ('projection', 'Projection Method'),
        ('h_alpha', 'H-Alpha Filter'),
        ('calcium_k', 'Calcium-K Filter'),
        ('white_light', 'White Light Filter'),
        ('coronagraph', 'Coronagraph'),
    ]
    
    solar_photo_method = models.CharField(
        max_length=20,
        choices=SOLAR_PHOTO_METHOD,
        blank=True,
        help_text="Method used for solar photography"
    )
    
    # Filter details
    filter_used = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Specific filter model/type used"
    )
    
    # Timestamp untuk sequence
    exact_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Exact time of capture"
    )
    
    # Additional technical details for eclipse photos
    is_composite = models.BooleanField(
        default=False,
        help_text="Is this a composite/stacked image?"
    )
    
    frame_count = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Number of frames if composite"
    )
    
    # Environmental conditions at capture
    ambient_temperature = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        null=True, 
        blank=True,
        help_text="Temperature at time of capture"
    )
    
    # Processing specifics for eclipse
    hdr_brackets = models.CharField(
        max_length=100,
        blank=True,
        help_text="HDR bracket range (e.g., -2, 0, +2 EV)"
    )
    
    title = models.CharField(max_length=200)
    """
    The title of the image.
    """
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    """
    The slug of the image.
    """
    image = models.ImageField(upload_to='astronomy/photos/%Y/%m/')
    """
    The image.
    """
    thumbnail = models.ImageField(upload_to='astronomy/thumbnails/', blank=True, null=True)
    """
    The thumbnail of the image.
    """
    
    #object info 
    celestial_objects = models.ForeignKey(CelestialObjects, on_delete=models.SET_NULL, null=True, blank =True)
    """
    The celestial object observed.
    """
    object_name = models.CharField(max_length=100)
    """
    The name of the celestial object.
    """
    
    #Technical details
    capture_date = models.DateTimeField()
    """
    The date and time of the observation.
    """
    exposure_time = models.CharField(max_length=50, blank=True, 
                                     help_text="e.g., 1/125s or 30s")
    """
    The exposure time of the image.
    """
    iso = models.IntegerField(null=True, blank=True)
    """
    The ISO of the image.
    """
    aperture = models.CharField(max_length=20,blank=True, help_text="e.g., f/8")
    """
    The aperture of the image.
    """
    focal_length = models.CharField(max_length=20,blank=True, 
                                    help_text="mm")
    """
    The focal length of the image.
    """
    frames = models.IntegerField(null=True, blank=True, help_text="Number of frames stacked")
    """
    The number of frames stacked.
    """
    
    # Equipment
    telescope = models.CharField(max_length=100, blank=True)
    """
    The telescope used for the observation.
    """
    camera = models.CharField(max_length=100, blank=True)
    """
    The camera used for the observation.
    """
    mount = models.CharField(max_length=100, blank=True)
    """
    The mount used for the observation.
    """
    
    #processing
    processing_software = models.CharField(max_length=100, blank=True)
    """
    The software used to process the image.
    """
    processing_notes = models.TextField(blank=True)
    """
    The notes about the processing of the image.
    """
    
    #related observation
    observation = models.ForeignKey(ObservationLog, on_delete=models.SET_NULL, null=True, blank =True, 
                                    related_name='photos')
    """
    The observation log related to the image.
    """
    research_project = models.ForeignKey(ResearchProject, on_delete=models.SET_NULL, null=True, blank =True, 
                                         related_name='photos')
    """
    The research project related to the image.
    """
    
    #meta data
    is_featured = models.BooleanField(default=False)
    """
    Whether the image is featured or not.
    """
    is_public = models.BooleanField(default=True)
    """
    Whether the image is public or not.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    """
    The date the image was created.
    """
    
    description = models.TextField(blank=True)
    
    is_processed = models.BooleanField(default=False)
    
    stacked_frames = models.IntegerField(null=True, blank=True, help_text="Number of frames stacked")
    
    sequence_number = models.IntegerField(null=True, blank=True,
                                          help_text="For time-series observations")
    
    class Meta:
        ordering = ['-capture_date', 'sequence_number']
        """
        The images are ordered by the capture date.
        """
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        """
        The slug is generated from the title.
        """
    
    def is_solar_eclipse(self):
        return self.eclipse_phase.startswith('solar_')
    
    def is_lunar_eclipse(self):
        return self.eclipse_phase.startswith('lunar_')
    
    def requires_safety_equipment(self):
        """Check if this photo type requires safety equipment"""
        dangerous_phases = ['solar_c1', 'solar_c2', 'solar_c4', 'solar_baileys']
        return self.eclipse_phase in dangerous_phases
        
    def __str__(self):
        return self.title
        """
        The string representation of the image.
        """

class EclipseObservation(models.Model):
    """Specialized Model For Eclipse Observations"""
    
    observation = models.OneToOneField(
        ObservationLog,
        on_delete=models.CASCADE,
        related_name='eclipse_data'
    )
    
    ECLIPSE_TYPES = [
        ('lunar_total', 'Lunar - Total'),
        ('lunar_partial', 'Lunar - Partial'),
        ('lunar_penumbral', 'Lunar - Penumbral'),
        ('solar_total', 'Solar - Total'),
        ('solar_partial', 'Solar - Partial'),
        ('solar_annular', 'Solar - Annular'),
        ('solar_hybrid', 'Solar - Hybrid'),
    ]
    
    eclipse_type = models.CharField(max_length=20, choices=ECLIPSE_TYPES)
    
    #safety equipment (untuk gerhana matahari)
    SOLAR_FILTERS = [
        ("",'Not Applicable'),
        ('solar_filter', 'Solar Filter'),
        ('eclipse_glasses', 'Eclipse Glasses'),
        ('welding_glass', 'Welding Glass #14'),
        ('mylar','Mylar Filter'),
        ('thousand_oaks', 'Thousand Oaks Solar Filter'),
        ('baader', 'Baader AstroSolar'),
        ('projection', 'Projection Method')
    ]
    
    safety_equipment = models.CharField(
        max_length=30,
        choices=SOLAR_FILTERS,
        blank=True,
        help_text="Critical for solar eclipses"
    )
    
    
    #Contact times (berbeda untuk solar vs lunar)
    c1_time = models.DateTimeField(null=True, blank=True, verbose_name="First Contact")
    c2_time = models.DateTimeField(null=True, blank=True, verbose_name="Second Contact")
    max_time = models.DateTimeField(null=True, blank=True, verbose_name="Maximum Eclipse")
    c3_time = models.DateTimeField(null=True, blank=True, verbose_name="Third Contact")
    c4_time = models.DateTimeField(null=True, blank=True, verbose_name="Fourth Contact")
    
    #lunar specific
    p1_time = models.DateTimeField(null=True, blank=True, verbose_name="Penumbra Start")
    u1_time = models.DateTimeField(null=True, blank=True, verbose_name="Umbra Start")
    u2_time = models.DateTimeField(null=True, blank=True, verbose_name="Total Start")
    u3_time = models.DateTimeField(null=True, blank=True, verbose_name="Total End")
    u4_time = models.DateTimeField(null=True, blank=True, verbose_name="Umbra End")
    p2_time = models.DateTimeField(null=True, blank=True, verbose_name="Penumbra End")
    
    
    #Danjon scale (lunar only)
    DANJON_SCALE =[
        ('','N/A'),
        ('L0', 'L0 - Very dark'),
        ('L1', 'L1 - Dark gray/brown'),
        ('L2', 'L2 - Deep red/rust'),
        ('L3', 'L3 - Brick red'),
        ('L4', 'L4 - Bright copper/orange'),
    ]
    
    danjon_scale = models.CharField(
        max_length=2,
        choices=DANJON_SCALE,
        blank = True,
        help_text="Brightness scale for total lunar eclipses (L0-L4)"
    )
    
    #solar specific measurement
    magnitude = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Eclipse magnitude (0-1 for partial, > for total)"
    )
    
    obscuration = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage of sun's area covered"
    )
    
    #Duration (for totality/annularity)
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Duration of totality/annularity in seconds"
    )
    
    #environtment observation
    temperatur_drop = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Temperature drop in Celsius"
    )
    
    #shadow band (solar)
    shadow_bands_observed = models.BooleanField(default=False)
    shadow_bands_notes = models.TextField(blank=True)
    
    #Baile's beads (solar)
    bailes_beads_observed = models.BooleanField(default=False)
    
    #diamond ring (solar)
    diamond_ring_observed = models.BooleanField(default=False)
    
    #corona observations (solar total)
    corona_shape = models.CharField(max_length=100, blank=True)
    corona_extent =models.CharField(max_length=100, blank=True)
    prominences_observed = models.BooleanField(default=False)
    prominences_notes = models.TextField(blank=True)
    
    #Animal behaviour 
    animal_behaviour_notes = models.TextField(
        blank=True,
        help_text="Notable animal/bird behavior during eclipse"

    )
    
    #general notes
    weather_impact = models.TextField(blank=True)
    viewing_success = models.IntegerField(
        null=True,
        blank=True,
        help_text="Success rate 0-100%"
    )
    
    class Meta:
        ordering = ['-observation__observation_date']
    
    
    def __str__(self):
        return f"{self.get_eclipse_type_display()} - {self.observation.observation_date.date()}"

    def is_solar(self):
        return self.eclipse_type.startswith('solar_')

    def is_lunar(self):
        return self.eclipse_type.startswith('lunar_')
    
    def is_total_lunar(self):
        return self.eclipse_type == 'lunar_total'


class ResearchTemplate(models.Model):
    """Pre-defined templates for common research types"""
    
    name = models.CharField(max_length=100,unique=True)
    research_type = models.CharField(max_length=20, choices=ResearchProject.RESEARCH_TYPES)
    description = models.TextField()
    
    # Template configuration
    # Example for Jupiter moons:
    # {
    #   "fields": [
    #     {"name": "io_position", "type": "float", "unit": "DJ", "label": "Io Position"},
    #     {"name": "europa_position", "type": "float", "unit": "DJ", "label": "Europa Position"},
    #     ...
    #   ],
    #   "analysis_types": ["period", "kepler"],
    #   "theoretical_values": {...}
    # }
    
    template_config = models.JSONField()
    
    instruction = models.TextField(help_text="Step-by-step guide for this research")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_jupiter_moons_template(cls):
        """Get or create Jupiter Moons orbital tracking template"""
        template, created = cls.objects.get_or_create(
            name="Jupiter Galilean Moons - Orbital Period",
            defaults={
                'research_type': 'orbital',
                'description': 'Track the orbital periods of Jupiter\'s 4 Galilean moons',
                'template_config': {
                    'fields': [
                        {'name': 'io_position', 'type': 'float', 'unit': 'DJ', 'label': 'Io Position (DJ)', 'required': False},
                        {'name': 'europa_position', 'type': 'float', 'unit': 'DJ', 'label': 'Europa Position (DJ)', 'required': False},
                        {'name': 'ganymede_position', 'type': 'float', 'unit': 'DJ', 'label': 'Ganymede Position (DJ)', 'required': False},
                        {'name': 'callisto_position', 'type': 'float', 'unit': 'DJ', 'label': 'Callisto Position (DJ)', 'required': False},
                    ],
                    'analysis_types': ['period', 'kepler'],
                    'theoretical_values': {
                        'io': {'period': 1.769, 'semi_major_axis': 421700},
                        'europa': {'period': 3.551, 'semi_major_axis': 671100},
                        'ganymede': {'period': 7.155, 'semi_major_axis': 1070400},
                        'callisto': {'period': 16.689, 'semi_major_axis': 1882700},
                    },
                    'minimum_observations': 14,
                    'recommended_duration': 30,
                },
                'instructions': """
1. Observe Jupiter every night at approximately the same time
2. Take photos/video showing Jupiter and all 4 moons
3. Measure position of each moon in Jupiter Diameters (DJ)
4. Positive = East, Negative = West
5. Record for minimum 14 days (30 days recommended)
6. Analysis will calculate orbital periods and verify Kepler's 3rd Law
                """,
                'is_active': True
            }
        )
        return template