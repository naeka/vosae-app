module.exports = (grunt) ->
  # Constants
  ACCOUNT_ROOT       = 'www/account/static/account'
  CORE_ROOT          = 'www/core/static/core'
  DOCS_ROOT          = 'www/docs/static/docs'
    
  ACCOUNT_BUILD_DIR  = "#{ACCOUNT_ROOT}/build/"
  CORE_BUILD_DIR     = "#{CORE_ROOT}/build/"
  DOCS_BUILD_DIR     = "#{DOCS_ROOT}/build/"
  
  CORE_JS_DIR        = "#{CORE_ROOT}/js/"

  ACCOUNT_SASS_DIR   = "#{ACCOUNT_ROOT}/sass/"
  CORE_SASS_DIR      = "#{CORE_ROOT}/sass/"
  DOCS_SASS_DIR      = "#{DOCS_ROOT}/sass/"
  
  ACCOUNT_CSS_DIR    = "#{ACCOUNT_ROOT}/css/"
  CORE_CSS_DIR       = "#{CORE_ROOT}/css/"
  DOCS_CSS_DIR       = "#{DOCS_ROOT}/css/"
  
  GLOB_SASS_FILES    = "**/*.sass"
  GLOB_CSS_FILES     = "**/*.css"
  GLOB_JS_FILES      = "**/*.js"

  # Configuration
  grunt.initConfig

    #
    # Minify js files using UglifyJS
    #
    uglify:
      options:
        report: "min"
        compress: true
      core_js:
        files:
          "www/core/static/core/build/core.min.js": [CORE_BUILD_DIR + "core.js"]

    #
    # Minify css files using clean-css
    #
    cssmin:
      options:
        report: "min"
        keepSpecialComments: "0"
      account:
        files:
          "www/account/static/account/build/account.min.css": [ACCOUNT_BUILD_DIR + "account.css"]
      core:
        files:
          "www/core/static/core/build/core.min.css": [CORE_BUILD_DIR + "core.css"]  
      docs:
        files:
          "www/docs/static/docs/build/docs.min.css": [DOCS_BUILD_DIR + "docs.css"]   

    #
    # Watch directories for changes
    #
    watch:
      options: 
        nospawn: true
      core_sass:
        files: [CORE_SASS_DIR + GLOB_SASS_FILES]
        tasks: ["compass:core", "concat:core_css"]
      core_css:
        files: [CORE_CSS_DIR + GLOB_CSS_FILES]
        tasks: ["concat:core_css"]
      core_js:
        files: [CORE_JS_DIR + GLOB_JS_FILES]
        tasks: ["concat:core_js"]
      account_sass:
        files: [ACCOUNT_SASS_DIR + GLOB_SASS_FILES]
        tasks: ["compass:account", "concat:account_css"]
      account_css:
        files: [ACCOUNT_CSS_DIR + GLOB_CSS_FILES]
        tasks: ["concat:account_css"]
      docs_sass:
        files: [DOCS_SASS_DIR + GLOB_SASS_FILES]
        tasks: ["compass:docs", "concat:docs_css"]
      docs_css:
        files: [DOCS_CSS_DIR + GLOB_CSS_FILES]
        tasks: ["concat:docs_css"]

    #
    # Concatenate files
    #
    concat:
      account_css:
        src: [
          ACCOUNT_CSS_DIR + "account.css"
        ]
        dest: ACCOUNT_BUILD_DIR + "account.css"
      core_css:
        src: [
          CORE_CSS_DIR + GLOB_CSS_FILES
        ]
        dest: CORE_BUILD_DIR + "core.css"
      core_js:
        src: [
          CORE_JS_DIR + "jquery.js"
          CORE_JS_DIR + "bootstrap.js"
        ]
        dest: CORE_BUILD_DIR + "core.js"
      docs_css:
        src: [
          DOCS_CSS_DIR + "pygments.css",
          DOCS_CSS_DIR + "docs.css"
        ]
        dest: DOCS_BUILD_DIR + "docs.css"

    #
    # Compass
    #
    compass:
      account:
        options:
          basePath: 'www/account/'
          config: 'www/account/config.rb'
          trace: true
      core:
        options:
          basePath: 'www/core/'
          config: 'www/core/config.rb'
          trace: true
      docs:
        options:
          basePath: 'www/docs/'
          config: 'www/docs/config.rb'
          trace: true
  
    #
    # Cleaning
    #
    clean:
      release: [
        ACCOUNT_SASS_DIR
        ACCOUNT_CSS_DIR
        CORE_JS_DIR
        CORE_SASS_DIR
        CORE_CSS_DIR
        DOCS_SASS_DIR
        DOCS_CSS_DIR
      ]

  #
  # Load tasks
  #
  grunt.loadNpmTasks 'grunt-contrib-watch'
  grunt.loadNpmTasks 'grunt-contrib-concat'
  grunt.loadNpmTasks 'grunt-contrib-uglify'
  grunt.loadNpmTasks 'grunt-contrib-compass'
  grunt.loadNpmTasks 'grunt-contrib-cssmin'
  grunt.loadNpmTasks 'grunt-contrib-clean'

  #
  # Register tasks
  # 
  grunt.registerTask 'default', ->
    grunt.task.run [
      'build-dev'
      'watch'
    ]

  grunt.registerTask 'build-dev', 'Development build', ->
    grunt.task.run [
      # Account
      'compass:account'
      'concat:account_css'

      # Core
      'compass:core'
      'concat:core_css'
      'concat:core_js'

      # Docs
      'compass:docs'
      'concat:docs_css'
    ]

  grunt.registerTask 'build-prod', 'Production build', ->
    grunt.config.set 'compass.account.options.force', true
    grunt.config.set 'compass.core.options.force', true
    grunt.config.set 'compass.docs.options.force', true
    grunt.task.run [
      'build-dev'

      # Account
      'cssmin:account'

      # Core
      'cssmin:core'
      'uglify:core_js'

      # Docs
      'cssmin:docs'

      # Cleaning
      'clean:release'
    ]